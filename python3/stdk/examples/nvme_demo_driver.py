import ctypes
import time
from types import SimpleNamespace

# Import objects we will use
from stdk.nvme.spec.registers.nvme_regs import NVMeRegisters
from stdk.nvme.spec.structures import CQE
from stdk.nvme.spec.commands.admin.identify import (IdentifyController,
                                                    IdentifyNamespace,
                                                    IdentifyNamespaceList)
from stdk.nvme.spec.commands.admin.create_io_completion_q import CreateIOCompletionQueue
from stdk.nvme.spec.commands.admin.create_io_submission_q import CreateIOSubmissionQueue


class NVMeDemoDriver:
    sq_entry_size = 64
    cq_entry_size = 16

    class NVMeQueue:
        def __init__(self, base_address, entries, entry_size):
            self.base_address = base_address
            self.entries = entries
            self.entry_size = entry_size
            self.current_slot = 0
            self.phase = 1

        def get_next_available_slot(self):
            # The next slot address in the queue is the base address plus the current
            #   index times the size of the queue entries
            next_slot_addr = self.base_address.vaddr + (self.current_slot * self.entry_size)

            #  TODO: Wait until the slot is available by looking at the head and tail

            # Increment and wrap if needed
            self.current_slot += 1
            if self.current_slot == self.entries:
                self.current_slot = 0
                self.phase = 0 if self.phase == 1 else 1

            return self.current_slot, next_slot_addr

    def __init__(self, nvme_device, mem_mgr):
        self.nvme_device = nvme_device
        self.mem_mgr = mem_mgr

        # Track CID
        self.cid = 0x1000

        # Track SQ/CQ indexes
        self.asq_index = 0
        self.asq_entries = 0
        self.acq_index = 0
        self.acq_entries = 0

        self.max_queues = 4096
        self.nvme_queues = [None] * self.max_queues

    def cc_disable(self, timeout_s=10):
        self.nvme_device.nvme_regs.CC.EN = 0
        for i in range(int(timeout_s * 1000)):
            if self.nvme_device.nvme_regs.CSTS.RDY == 0:
                break
            time.sleep(1 / 1000)
        else:
            assert False, 'Device never disabled'

    def cc_enable(self, timeout_s=10):
        self.nvme_device.nvme_regs.CC.EN = 1
        for i in range(int(timeout_s * 1000)):
            if self.nvme_device.nvme_regs.CSTS.RDY == 1:
                break
            time.sleep(1 / 1000)
        else:
            assert False, 'Device never enabled'

    def init_admin_queues(self, asq_entries=64, acq_entries=256):
        # Make sure the device is disabled before messing with queues
        self.cc_disable()

        # Allocate enough memory for the requested queue size based on
        #   SQ entry size of 64 bytes and CQ entry size of 16 bytes
        iova_start = 0x71000000

        self.asq_mem = self.mem_mgr.malloc(NVMeDemoDriver.sq_entry_size * asq_entries)
        self.asq_entries = asq_entries
        self.acq_mem = self.mem_mgr.malloc(NVMeDemoDriver.cq_entry_size * acq_entries)
        self.acq_entries = acq_entries

        # Map the user space addresses into our own "made up" iova's
        self.asq_mem.iova = iova_start
        self.acq_mem.iova = self.asq_mem.iova + self.asq_mem.size

        # Map ASQ memory with the device so it is allowed to only READ from it
        self.nvme_device.map_dma_region_read(self.asq_mem.vaddr,
                                             self.asq_mem.iova,
                                             self.asq_mem.size)

        # Map ACQ memory with the device so it is allowed to only WRITE to it
        self.nvme_device.map_dma_region_write(self.acq_mem.vaddr,
                                              self.acq_mem.iova,
                                              self.acq_mem.size)

        # Stop the device from mastering the bus while we set admin queues up
        self.nvme_device.pcie_regs.CMD.BME = 0

        # Set up our ADMIN queues
        self.nvme_device.nvme_regs.AQA.ASQS = asq_entries - 1  # Zero based
        self.nvme_device.nvme_regs.ASQ.ASQB = self.asq_mem.iova
        self.nvme_device.nvme_regs.AQA.ACQS = acq_entries - 1  # Zero based
        self.nvme_device.nvme_regs.ACQ.ACQB = self.acq_mem.iova

        # Set up CC
        self.nvme_device.nvme_regs.CC = NVMeRegisters.Cc(0)
        self.nvme_device.nvme_regs.CC.IOSQES = 6  # 2 ** 6 = 64 bytes per command entry
        self.nvme_device.nvme_regs.CC.IOCQES = 4  # 2 ** 4 = 16 bytes per completion entry

        # Re-enable BME so the device can master the bus
        self.nvme_device.pcie_regs.CMD.BME = 1

        # Save the admin queue as qid = 0
        self.nvme_queues[0] = (NVMeDemoDriver.NVMeQueue(self.asq_mem, self.asq_entries,
                                                        NVMeDemoDriver.sq_entry_size),
                               NVMeDemoDriver.NVMeQueue(self.acq_mem, self.acq_entries,
                                                        NVMeDemoDriver.cq_entry_size))

    def init_io_queues(self, num_queues=10, queue_entries=256):

        # Has the ADMIN queue been initialized?
        assert self.nvme_device.nvme_regs.AQA.ASQS != 0, 'admin queues are NOT initialized!'
        assert self.nvme_device.nvme_regs.ASQ.ASQB != 0, 'admin queues are NOT initialized!'
        assert self.nvme_device.nvme_regs.AQA.ACQS != 0, 'admin queues are NOT initialized!'
        assert self.nvme_device.nvme_regs.ACQ.ACQB != 0, 'admin queues are NOT initialized!'

        # Pick iova address base for queues
        iommu_iova = 0x81000000

        # Create each queue requested
        for queue_id in range(1, num_queues + 1):

            # Allocate memory for the completion queue, and map with for write with the iommu
            compl_q_mem = self.mem_mgr.malloc(NVMeDemoDriver.cq_entry_size * queue_entries)
            compl_q_mem.iova = iommu_iova
            iommu_iova += compl_q_mem.size
            self.nvme_device.map_dma_region_write(compl_q_mem.vaddr,
                                                  compl_q_mem.iova,
                                                  compl_q_mem.size)

            # Create the CreateIOCompletionQueue command
            create_iocq_cmd = CreateIOCompletionQueue()
            create_iocq_cmd.DPTR.PRP.PRP1 = compl_q_mem.iova
            create_iocq_cmd.QSIZE = queue_entries - 1  # zero-based value
            create_iocq_cmd.QID = queue_id
            create_iocq_cmd.IV = 0  # Interrupts are for suckers
            create_iocq_cmd.IEN = 0  # Interrupts are for suckers
            create_iocq_cmd.PC = 1

            # Send the command and wait for a completion
            cqe = self.sync_cmd(create_iocq_cmd)
            assert cqe.SF.SC == 0

            # Allocate memory for the submission queue, and map with for read with the iommu
            sub_q_mem = self.mem_mgr.malloc(NVMeDemoDriver.sq_entry_size * queue_entries)
            sub_q_mem.iova = iommu_iova
            iommu_iova += sub_q_mem.size
            self.nvme_device.map_dma_region_read(sub_q_mem.vaddr,
                                                 sub_q_mem.iova,
                                                 sub_q_mem.size)

            # Create the command
            create_iosq_cmd = CreateIOSubmissionQueue()
            create_iosq_cmd.DPTR.PRP.PRP1 = sub_q_mem.iova
            create_iosq_cmd.QSIZE = queue_entries - 1  # zero-based value
            create_iosq_cmd.QID = queue_id
            create_iosq_cmd.CQID = queue_id
            create_iosq_cmd.QPRIO = 0
            create_iosq_cmd.PC = 1
            create_iosq_cmd.NVMSETID = 0

            # Send the command and wait for a completion
            cqe = self.sync_cmd(create_iosq_cmd, timeout_s=1)
            assert cqe.SF.SC == 0

            # Save the queue
            self.nvme_queues[queue_id] = (NVMeDemoDriver.NVMeQueue(sub_q_mem, queue_entries,
                                                                   NVMeDemoDriver.sq_entry_size),
                                          NVMeDemoDriver.NVMeQueue(compl_q_mem, queue_entries,
                                                                   NVMeDemoDriver.cq_entry_size))

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

    def get_namespace_info(self):

        # Send an Identify controller command, check response
        id_ctrl_cmd = IdentifyController()
        cqe = self.sync_cmd(id_ctrl_cmd)
        assert cqe.SF.SC == 0, 'Command failed with SF.SC = 0x{:x}'.format(cqe.SF.SC)
        self.nvme_device.identify_controller_data = id_ctrl_cmd.data_in

        # Send an Indentify Namespace List command to get all used namespaces
        id_ns_list_cmd = IdentifyNamespaceList()
        cqe = self.sync_cmd(id_ns_list_cmd)
        assert cqe.SF.SC == 0, 'Command failed with SF.SC = 0x{:x}'.format(cqe.SF.SC)

        # Loop through all active namespaces and send each one IdentifyNamespace commands
        self.nvme_device.namespaces = [None] * 1024

        for ns_id in [id_ns_list_cmd.data_in.Identifiers[i] for
                      i in range(1024)
                      if id_ns_list_cmd.data_in.Identifiers[i] != 0]:

            ns = SimpleNamespace(NSID=ns_id)

            # Send an Identify Namespace command, check response
            id_ns_cmd = IdentifyNamespace(NSID=ns_id)
            cqe = self.sync_cmd(id_ns_cmd)
            assert cqe.SF.SC == 0, 'Command failed with SF.SC = 0x{:x}'.format(cqe.SF.SC)
            ns.identify_namespace_data = id_ns_cmd.data_in

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

            self.nvme_device.namespaces[ns_id] = ns

    def sync_cmd(self, command, timeout_s=10):

        if command.cmdset_admin:
            sqid = 0
            cqid = 0
        else:
            # Just pick the first one for now
            sqid = 1
            cqid = 1

        assert self.nvme_queues[sqid] is not None
        sq = self.nvme_queues[sqid][0]
        cq = self.nvme_queues[cqid][1]

        if command.data_in is not None and command.data_in.size > 0:

            # Allocate memory for the command
            cmd_mem = self.mem_mgr.malloc(command.data_in.size)
            cmd_mem.iova = 0x91000000

            # Map CMD memory with the device so it is allowed to READ and WRITE
            self.nvme_device.map_dma_region_rw(cmd_mem.vaddr,
                                               cmd_mem.iova,
                                               cmd_mem.size)

            # Add the address for the command data in
            command.DPTR.PRP.PRP1 = cmd_mem.iova

        # Set a CID for the command
        command.CID = self.cid
        self.cid += 1

        # Post the command on the next available sq slot
        sq_tail, sq_addr = sq.get_next_available_slot()
        ctypes.memmove(sq_addr, ctypes.addressof(command), NVMeDemoDriver.sq_entry_size)

        # Hit the doorbell
        self.nvme_device.nvme_regs.SQNDBS[sqid].SQTAIL = sq_tail

        # Figure out where the next completion should be coming to
        cq_head, cq_addr = cq.get_next_available_slot()
        cqe = CQE.from_address(cq_addr)

        # Wait for the completion by polling for the phase bit change
        for i in range(int(timeout_s * 1000)):
            if cqe.SF.P == cq.phase:
                break
            time.sleep(1 / 1000)
        else:
            assert False, 'Command did not complete'

        # Advance the CQ head so the device knows we are done with it
        self.nvme_device.nvme_regs.SQNDBS[sqid].CQHEAD = cq_head

        # Fill in the data in for the command
        if command.data_in is not None and command.data_in.size > 0:
            ctypes.memmove(ctypes.addressof(command.data_in), cmd_mem.vaddr, command.data_in.size)
            self.nvme_device.unmap_dma_region(cmd_mem.iova, cmd_mem.size)
            self.mem_mgr.free(cmd_mem)

        return cqe
