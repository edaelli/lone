import ctypes
import time

from types import SimpleNamespace

from lone.system import System, DMADirection
from lone.injection import Injection
from lone.nvme.spec.queues import QueueMgr, NVMeSubmissionQueue, NVMeCompletionQueue
from lone.nvme.spec.prp import PRP
from lone.nvme.spec.structures import CQE
from lone.nvme.spec.commands.admin.identify import (IdentifyController,
                                                    IdentifyNamespace,
                                                    IdentifyNamespaceList,
                                                    IdentifyUUIDList)
from lone.nvme.spec.commands.admin.create_io_completion_q import CreateIOCompletionQueue
from lone.nvme.spec.commands.admin.create_io_submission_q import CreateIOSubmissionQueue
from lone.nvme.spec.commands.admin.delete_io_completion_q import DeleteIOCompletionQueue
from lone.nvme.spec.commands.admin.delete_io_submission_q import DeleteIOSubmissionQueue
from lone.nvme.spec.commands.status_codes import status_codes, NVMeStatusCodeException

import logging
logger = logging.getLogger('nvme_device')


class NVMeDeviceCommon:
    sq_entry_size = 64
    cq_entry_size = 16

    class CidMgr:
        def __init__(self, init_value=0x1000, max_value=0xFFFE):
            self.init_value = init_value
            self.max_value = max_value
            self.value = self.init_value

        def get(self):
            value = self.value

            self.value = self.value + 1
            if self.value >= self.max_value:
                self.value = self.init_value

            return value

    def __init__(self):
        # Base class must create and initialize the pci_regs before
        #   calling this init
        self.pcie_regs.init_capabilities()

        #  Store our MPS for easy access
        self.mps = 2 ** (12 + self.nvme_regs.CC.MPS)

        # CID manager
        self.cid_mgr = NVMeDeviceCommon.CidMgr()

        # NVMe Queue manager
        self.queue_mgr = QueueMgr()

        # List of outstanding commands
        self.outstanding_commands = []

        # Injectors
        self.injectors = Injection()

    def cc_disable(self, timeout_s=10):
        start_time = time.time()
        self.nvme_regs.CC.EN = 0
        while True:
            if (time.time() - start_time) > timeout_s:
                assert False, 'Device did not disable in {}s'.format(timeout_s)
            elif self.nvme_regs.CSTS.CFS == 1:
                logger.error('Disabling while CFS=1, not watiting for RDY=1')
                break
            elif self.nvme_regs.CSTS.RDY == 0:
                break
            time.sleep(0)

        # Clear all doorbells
        for sqdnbs in self.nvme_regs.SQNDBS:
            sqdnbs.SQTAIL = 0
            sqdnbs.CQHEAD = 0

    def cc_enable(self, timeout_s=10):
        start_time = time.time()
        self.nvme_regs.CC.EN = 1

        while True:
            if (time.time() - start_time) > timeout_s:
                assert False, 'Device did not enable in {}s'.format(timeout_s)
            elif self.nvme_regs.CSTS.RDY == 1:
                break
            time.sleep(0)

    def init_admin_queues(self, asq_entries=64, acq_entries=256):
        # Make sure the device is disabled before messing with queues
        self.cc_disable()

        self.asq_mem = self.malloc_and_map_iova(NVMeDeviceCommon.sq_entry_size * asq_entries,
                                                DMADirection.HOST_TO_DEVICE,
                                                client='asq')

        self.acq_mem = self.malloc_and_map_iova(NVMeDeviceCommon.cq_entry_size * acq_entries,
                                                DMADirection.DEVICE_TO_HOST,
                                                client='acq')

        # Stop the device from mastering the bus while we set admin queues up
        self.pcie_regs.CMD.BME = 0

        # Set up our ADMIN queues
        self.nvme_regs.AQA.ASQS = asq_entries - 1  # Zero based
        self.nvme_regs.ASQ.ASQB = self.asq_mem.iova
        self.nvme_regs.AQA.ACQS = acq_entries - 1  # Zero based
        self.nvme_regs.ACQ.ACQB = self.acq_mem.iova

        # Set up CC
        self.nvme_regs.CC.IOSQES = 6  # 2 ** 6 = 64 bytes per command entry
        self.nvme_regs.CC.IOCQES = 4  # 2 ** 4 = 16 bytes per completion entry

        # Enable all command sets supported by the device
        if self.nvme_regs.CAP.CSS == 0x40:
            self.nvme_regs.CC.CSS = 0x06

        # Re-enable BME so the device can master the bus
        self.pcie_regs.CMD.BME = 1

        # Add the Admin queue pair
        self.queue_mgr.add(NVMeSubmissionQueue(
                           self.asq_mem,
                           asq_entries,
                           NVMeDeviceCommon.sq_entry_size,
                           0,
                           ctypes.addressof(self.nvme_regs.SQNDBS[0])),
                           NVMeCompletionQueue(self.acq_mem,
                           acq_entries,
                           NVMeDeviceCommon.cq_entry_size,
                           0,
                           ctypes.addressof(self.nvme_regs.SQNDBS[0]) + 4))

    def init_io_queues(self, num_queues=10, queue_entries=256, sq_nvme_set_id=0):

        # Has the ADMIN queue been initialized?
        assert self.nvme_regs.AQA.ASQS != 0, 'admin queues are NOT initialized!'
        assert self.nvme_regs.ASQ.ASQB != 0, 'admin queues are NOT initialized!'
        assert self.nvme_regs.AQA.ACQS != 0, 'admin queues are NOT initialized!'
        assert self.nvme_regs.ACQ.ACQB != 0, 'admin queues are NOT initialized!'

        # Create each queue requested
        for queue_id in range(1, num_queues + 1):

            # Allocate memory for the completion queue, and map with for write with the iommu
            compl_q_mem = self.malloc_and_map_iova(NVMeDeviceCommon.cq_entry_size * queue_entries,
                                                   DMADirection.DEVICE_TO_HOST,
                                                   client='iocq_{}'.format(queue_id))

            # Create the CreateIOCompletionQueue command
            create_iocq_cmd = CreateIOCompletionQueue()
            create_iocq_cmd.DPTR.PRP.PRP1 = compl_q_mem.iova
            create_iocq_cmd.QSIZE = queue_entries - 1  # zero-based value
            create_iocq_cmd.QID = queue_id
            create_iocq_cmd.IV = 0  # Interrupts are for suckers
            create_iocq_cmd.IEN = 0  # Interrupts are for suckers
            create_iocq_cmd.PC = 1

            # Send the command and wait for a completion
            self.sync_cmd(create_iocq_cmd)

            # Allocate memory for the submission queue, and map with for read with the iommu
            sub_q_mem = self.malloc_and_map_iova(NVMeDeviceCommon.sq_entry_size * queue_entries,
                                                 DMADirection.HOST_TO_DEVICE,
                                                 client='iosq_{}'.format(queue_id))

            # Create the command
            create_iosq_cmd = CreateIOSubmissionQueue()
            create_iosq_cmd.DPTR.PRP.PRP1 = sub_q_mem.iova
            create_iosq_cmd.QSIZE = queue_entries - 1  # zero-based value
            create_iosq_cmd.QID = queue_id
            create_iosq_cmd.CQID = queue_id
            create_iosq_cmd.QPRIO = 0
            create_iosq_cmd.PC = 1
            create_iosq_cmd.NVMSETID = sq_nvme_set_id

            # Send the command and wait for a completion
            self.sync_cmd(create_iosq_cmd, timeout_s=1)

            # Add the NVM queue pair
            self.queue_mgr.add(NVMeSubmissionQueue(
                               sub_q_mem,
                               queue_entries,
                               NVMeDeviceCommon.sq_entry_size,
                               queue_id,
                               ctypes.addressof(self.nvme_regs.SQNDBS[0]) + (queue_id * 8)),
                               NVMeCompletionQueue(
                               compl_q_mem,
                               queue_entries,
                               NVMeDeviceCommon.cq_entry_size,
                               queue_id,
                               ctypes.addressof(self.nvme_regs.SQNDBS[0]) + ((queue_id * 8) + 4)))

    def free_io_queues(self):

        # First delete all submission queuees
        for (sqid, cqid), (sq, cq) in self.queue_mgr.nvme_queues.items():

            # Never delete Admin queues
            if sqid == 0 and cqid == 0:
                continue

            # Delete IO submission queue
            del_sq_cmd = DeleteIOSubmissionQueue(QID=sqid)
            self.sync_cmd(del_sq_cmd, timeout_s=1)

        # Then delete all completion queuees
        for (sqid, cqid), (sq, cq) in self.queue_mgr.nvme_queues.items():

            # Never delete Admin queues
            if sqid == 0 and cqid == 0:
                continue

            # Delete IO completion queue
            del_cq_cmd = DeleteIOCompletionQueue(QID=cqid)
            self.sync_cmd(del_cq_cmd, timeout_s=1)

    def ns_size(self, lba_ds_bytes, nsze, nuse):

        unit = 'B'
        divisor = 1
        usage = lba_ds_bytes * nuse
        total = lba_ds_bytes * nsze

        if total < (10 ** 3):
            unit = 'B'
            divisor = 1
        elif total < (10 ** 6):
            unit = 'KB'
            divisor = (10 ** 3)
        elif total < (10 ** 9):
            unit = 'MB'
            divisor = (10 ** 6)
        elif total < (10 ** 12):
            unit = 'GB'
            divisor = (10 ** 9)
        else:
            unit = 'TB'
            divisor = (10 ** 12)

        usage = round(((lba_ds_bytes * nuse) / divisor), 2)
        total = round(((lba_ds_bytes * nsze) / divisor), 2)

        return usage, total, unit

    def lba_ds_size(self, lba_ds_bytes):

        unit = 'B'
        divisor = 1

        if lba_ds_bytes > 1024:
            unit = 'KiB'
            divisor = 1024

        size = lba_ds_bytes // divisor
        return size, unit

    def identify_namespaces(self):

        # Send an Indentify Namespace List command to get all used namespaces
        id_ns_list_cmd = IdentifyNamespaceList()
        self.sync_cmd(id_ns_list_cmd)

        # Loop through all active namespaces and send each one IdentifyNamespace commands
        namespaces = [None] * 1024

        for ns_id in [id_ns_list_cmd.data_in.Identifiers[i] for
                      i in range(1024)
                      if id_ns_list_cmd.data_in.Identifiers[i] != 0]:

            # Create an object with namespace data
            ns = SimpleNamespace(NSID=ns_id)

            # Send an Identify Namespace command, check response
            id_ns_cmd = IdentifyNamespace(NSID=ns_id)
            self.sync_cmd(id_ns_cmd)
            ns.id_ns_data = id_ns_cmd.data_in

            # Get information on supported LBAF formats for this namespace
            ns.nsze = id_ns_cmd.data_in.NSZE
            ns.nuse = id_ns_cmd.data_in.NUSE
            ns.flbas = id_ns_cmd.data_in.FLBAS
            ns.lba_ds = id_ns_cmd.data_in.LBAF_TBL[ns.flbas].LBADS
            ns.ms_bytes = id_ns_cmd.data_in.LBAF_TBL[ns.flbas].MS
            assert ns.lba_ds != 0, 'Invalid LBADS = 0'

            # From the identify namespace data we can calculate some information to
            #   present to the user

            # LBA data size in bytes
            ns.lba_ds_bytes = 2 ** ns.lba_ds
            ns.ns_usage, ns.ns_total, ns.ns_unit = self.ns_size(ns.lba_ds_bytes, ns.nsze, ns.nuse)
            ns.lba_size, ns.lba_unit = self.lba_ds_size(ns.lba_ds_bytes)

            namespaces[ns_id] = ns

        return id_ns_list_cmd.data_in, namespaces

    def identify_uuid_list(self):
        id_uuid_list_cmd = IdentifyUUIDList()
        try:
            self.sync_cmd(id_uuid_list_cmd)
        except NVMeStatusCodeException:
            logger.info('Device failed id uuid list command!')
        self.uuid_list = id_uuid_list_cmd.data_in

    def identify_controller(self):
        # Send an Identify controller command, check response
        id_ctrl_cmd = IdentifyController()
        self.sync_cmd(id_ctrl_cmd)
        return id_ctrl_cmd.data_in

    def identify(self):
        ''' Tries to send as many identify commands as possible and builds up internal
            structures to be used later
        '''
        # Keep all controller identify data in a dictionary
        self.identify_data = {}
        self.identify_data['controller'] = self.identify_controller()
        self.identify_data['namespaces'], self.namespaces = self.identify_namespaces()
        self.identify_data['uuid_list'] = self.identify_uuid_list()

    def post_command(self, command):

        # Set a CID for the command
        command.CID = self.cid_mgr.get()

        # Post the command on the next available sq slot
        command.sq.post_command(command)

        # Keep track of outstanding commands
        self.outstanding_commands.append(command)

        command.start_time_ns = time.perf_counter_ns()

    def process_completions(self, cqids=None, max_completions=1, max_time_s=0):

        if cqids is None:
            cqids = self.queue_mgr.all_cqids
        else:
            if type(cqids) is int:
                cqids = [cqids]

        max_time = time.time() + max_time_s
        num_completions = 0
        while True:

            for cqid in cqids:
                if self.get_completion(cqid) is True:
                    num_completions += 1

            if num_completions >= max_completions:
                break

            if time.time() > max_time:
                break

            time.sleep(0.000001)

        return num_completions

    def get_completion(self, cqid):

        if cqid == 0:
            _, cq = self.queue_mgr.get(0, 0)
        else:
            _, cq = self.queue_mgr.get(None, cqid)

        # Figure out where the next completion should be coming to
        cqe = cq.get_next_completion()

        # Wait for the completion by polling for the phase bit change
        if cqe.SF.P == cq.phase:

            # Find outstanding command
            for command in self.outstanding_commands:
                if command.posted is True and command.CID == cqe.CID and command.sq.qid == cqe.SQID:

                    # Mark the time the command was completed as soon as we find it!
                    command.end_time_ns = time.perf_counter_ns()

                    command.posted = False
                    command.complete = True
                    ctypes.memmove(ctypes.addressof(command.cqe),
                                   ctypes.addressof(cqe),
                                   ctypes.sizeof(CQE))

                    # Remove from our outstanding_commands list
                    self.outstanding_commands.remove(command)

                    # Copy command memory to command.data_in and free the memory we used
                    if command.internal_mem is True:
                        self.free_cmd_memory(command)
                        command.internal_mem = False

                    # Consume the completion we just processed in the queue
                    cq.consume_completion()

                    # Advance the SQ head for the command based on what is on the completion
                    command.sq.head.set(cqe.SQHD)

                    return True
            else:
                assert False, 'Found a completion for a command that is not outstanding!'

        return False

    def sync_cmd(self, command, sqid=None, cqid=None, timeout_s=10, alloc_mem=True, check=True):
        # Start the command
        self.start_cmd(command, sqid, cqid, alloc_mem)

        # Wait for a completion
        self.process_completions(command.cq.qid, 1, timeout_s)

        # Make sure it is in complete state
        assert command.complete is True

        # Check for successful completion, will raise if not success
        if check:
            status_codes.check(command)

    def start_cmd(self, command, sqid=None, cqid=None, alloc_mem=True):

        if (command in self.outstanding_commands and
                command.posted is True and
                command.complete is False):
            assert False, 'Command already with the drive'

        if sqid is None:
            if command.cmdset_admin:
                sqid = 0
            else:
                sqid = self.queue_mgr.next_iosq_id()

        # Get command queues
        command.sq, command.cq = self.queue_mgr.get(sqid, cqid)

        # Allocate memory for command
        if alloc_mem is True:
            self.alloc_cmd_memory(command)
            command.internal_mem = True

        # Post the command on the next available sq slot
        self.post_command(command)
        command.posted = True

        # Return the qpair in which the command was posted
        return sqid, cqid

    def alloc_cmd_memory(self, command):
        size = 0
        direction = None

        if command.data_in is not None and command.data_out is not None:
            assert False, 'Data IN and OUT not yet supported!'

        elif command.__class__.__name__ == 'Write':
            direction = DMADirection.HOST_TO_DEVICE
            size = (command.NLB + 1) * self.namespaces[command.NSID].lba_ds_bytes

        elif command.__class__.__name__ == 'Read':
            direction = DMADirection.DEVICE_TO_HOST
            size = (command.NLB + 1) * self.namespaces[command.NSID].lba_ds_bytes

        elif command.data_in is not None and command.data_in.size > 0:
            direction = DMADirection.DEVICE_TO_HOST
            size = command.data_in.size

        elif command.data_out is not None and command.data_out.size > 0:
            direction = DMADirection.HOST_TO_DEVICE
            size = command.data_out.size

        else:
            # Just a command that doesnt send or receive data
            pass

        if size != 0:
            # TODO: Implement copying data from/to more than 1 PRP
            assert size <= (2 * 1024 * 1024), 'Support for PRPs larger than 2M not implemented!'

            # Get a PRP for the data
            data_prp = PRP(size, self.mps)
            data_prp.alloc(self, direction)

            # If we are sending data to the device, copy it over here
            if command.data_out is not None and direction == DMADirection.HOST_TO_DEVICE:
                assert size <= self.mps, 'Copying of more than MPS not yet supported'
                ctypes.memmove(data_prp.prp1_mem.vaddr,
                               ctypes.addressof(command.data_out),
                               command.data_out.size)

            # Add it to the command so we can track it/free it
            command.prps.append(data_prp)

            # Fill in the command's PRPs
            command.DPTR.PRP.PRP1 = data_prp.prp1
            command.DPTR.PRP.PRP2 = data_prp.prp2

    def free_cmd_memory(self, command):

        # If we got data from the device, copy it over here
        if command.data_in is not None and command.data_in.size > 0 and len(command.prps):
            assert command.data_in.size <= self.mps, 'Copying of more than MPS not yet supported'
            ctypes.memmove(ctypes.addressof(command.data_in),
                           command.prps[0].prp1_mem.vaddr,
                           command.data_in.size)

        # TODO: Implement copying data from/to more than 1 PRP
        assert len(command.prps) <= 1, 'More than 1 PRP not yet supported!'

        for prp in command.prps:
            prp.free_all_memory()
            command.prps.remove(prp)


def NVMeDevice(pci_slot):
    ''' Helper function to allow tests/modules/etc to pick a physical or simulated
        device by using the special nvsim pci_slot name. Any other name is treated
        as a real device in the pci bus
    '''
    if pci_slot == 'nvsim':
        from nvsim import NVMeSimulator
        return NVMeSimulator(pci_slot)
    else:
        return NVMeDevicePhysical(pci_slot)


class NVMeDevicePhysical(NVMeDeviceCommon):
    ''' Implementation that accesses a physical nvme device on the
          pcie bus via vfio
    '''
    def __init__(self, pci_slot):
        # Save off our slot
        self.pci_slot = pci_slot

        # Create the PCI Userspace device interface object
        self.pci_userspace_dev_ifc = System.PciUserspaceDevice(pci_slot)

        # Create the object to access PCIe registers
        self.pcie_regs = self.pci_userspace_dev_ifc.pci_regs()

        # Create the object to access NVMe registers
        self.nvme_regs = self.pci_userspace_dev_ifc.nvme_regs()

        # Initialize common
        super().__init__()

        # Create a memory manager object for this device
        self.mem_mgr = System.MemoryMgr(self.mps)

    def malloc_and_map_iova(self, num_bytes, direction, client='malloc_and_map_iova'):
        # Allocate memory
        mem = self.mem_mgr.malloc(num_bytes, client=client)

        # Map the vaddr to an iova with the device
        if direction == DMADirection.HOST_TO_DEVICE:
            self.pci_userspace_dev_ifc.map_dma_region_read(mem.vaddr, mem.iova, mem.size)
        elif direction == DMADirection.DEVICE_TO_HOST:
            self.pci_userspace_dev_ifc.map_dma_region_write(mem.vaddr, mem.iova, mem.size)
        else:
            assert False, 'Direction {} not yet supported!'.format(direction)

        # Return it
        return mem

    def free_and_unmap_iova(self, memory):
        # Unmap IOVA
        self.pci_userspace_dev_ifc.unmap_dma_region(memory.iova, memory.size)

        # Free memory
        self.mem_mgr.free(memory)
