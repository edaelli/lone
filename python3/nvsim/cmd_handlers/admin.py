import ctypes

from nvsim.cmd_handlers import NvsimCommandHandlers

from lone.nvme.spec.prp import PRP
from lone.nvme.spec.commands.status_codes import status_codes
from lone.system import MemoryLocation
from lone.nvme.device import NVMeDeviceCommon
from lone.nvme.spec.queues import NVMeSubmissionQueue, NVMeCompletionQueue

from lone.nvme.spec.commands.admin.identify import (Identify,
                                                    IdentifyData,
                                                    IdentifyController,
                                                    IdentifyNamespace,
                                                    IdentifyNamespaceList,
                                                    IdentifyUUIDList)
from lone.nvme.spec.commands.admin.create_io_completion_q import CreateIOCompletionQueue
from lone.nvme.spec.commands.admin.create_io_submission_q import CreateIOSubmissionQueue
from lone.nvme.spec.commands.admin.format_nvm import FormatNVM

import logging
logger = logging.getLogger('nvsim_admin')


class NVSimIdentify:
    OPC = Identify().OPC

    def __call__(self, nvsim_state, command, sq, cq):

        # Cast the command into a identify command
        id_cmd = Identify.from_buffer(command)
        logger.debug('NVMeAdminCommandHandler: {} CNS: 0x{:x}'.format(
            self.__class__.__name__, id_cmd.CNS))

        # Create the PRP at the location from the command
        prp = PRP(IdentifyData.size, nvsim_state.mps).from_address(id_cmd.DPTR.PRP.PRP1)

        # Based on CNS, we have to simulate different structures for responses
        if id_cmd.CNS == IdentifyController().CNS:
            prp.set_data_buffer(bytearray(nvsim_state.identify_controller_data()))
            status_code = status_codes['Successful Completion']

        elif id_cmd.CNS == IdentifyNamespace().CNS:
            try:
                prp.set_data_buffer(bytearray(nvsim_state.identify_namespace_data(id_cmd.NSID)))
                status_code = status_codes['Successful Completion']
            except IndexError:
                status_code = status_codes['Invalid Namespace or Format']

        elif id_cmd.CNS == IdentifyNamespaceList().CNS:
            prp.set_data_buffer(bytearray(nvsim_state.identify_namespace_list_data()))
            status_code = status_codes['Successful Completion']

        elif id_cmd.CNS == IdentifyUUIDList().CNS:
            prp.set_data_buffer(bytearray(nvsim_state.identify_uuid_list_data()))
            status_code = status_codes['Successful Completion']

        else:
            # Return invalid field in command in SF.SC
            logger.info('Identify command with CNS: 0x{:x} not supported'.format(id_cmd.CNS))
            status_code = status_codes['Invalid Field in Command']

        # Complete the command
        self.complete(command, sq, cq, status_code)


class NVSimCreateIOCompletionQueue:
    OPC = CreateIOCompletionQueue().OPC

    def __call__(self, nvsim_state, command, sq, cq):

        # Cast the command into a CreateIOCompletionQueue comma1d
        ccq_cmd = CreateIOCompletionQueue.from_buffer(command)

        if ccq_cmd.PC != 1:
            self.complete(command, sq, cq, status_codes['Invalid Field in Command'])
            return

        # Create the memory object for the queue location
        q_mem = MemoryLocation(ccq_cmd.DPTR.PRP.PRP1,
                               ccq_cmd.DPTR.PRP.PRP1,
                               (ccq_cmd.QSIZE + 1) * NVMeDeviceCommon.cq_entry_size,
                               'nvsim_iocq')

        # Make sure we can access the queue memory before actually doing it
        nvsim_state.check_mem_access(q_mem)

        # Add IO queue to nvsim_state's queue mgr
        new_cq = NVMeCompletionQueue(q_mem,
                                     ccq_cmd.QSIZE + 1,
                                     NVMeDeviceCommon.cq_entry_size,
                                     ccq_cmd.QID,
                                     (ctypes.addressof(
                                         nvsim_state.nvme_regs.SQNDBS[0]) +
                                         ((ccq_cmd.QID * 8) + 4)))

        # Keep it in our state tracker until it can be used with a SQ
        nvsim_state.completion_queues.append(new_cq)
        self.complete(command, sq, cq, status_codes['Successful Completion'])


class NVSimCreateIOSubmissionQueue:
    OPC = CreateIOSubmissionQueue().OPC

    def __call__(self, nvsim_state, command, sq, cq):

        # Cast the command into a CreateIOCompletionQueue command
        csq_cmd = CreateIOSubmissionQueue.from_buffer(command)

        # Create the memory object for the queue location
        q_mem = MemoryLocation(csq_cmd.DPTR.PRP.PRP1,
                               csq_cmd.DPTR.PRP.PRP1,
                               (csq_cmd.QSIZE + 1) * NVMeDeviceCommon.sq_entry_size,
                               'nvsim_iosq')

        # Make sure we can access the queue memory before actually doing it
        nvsim_state.check_mem_access(q_mem)

        # Create the sq object
        new_sq = NVMeSubmissionQueue(q_mem,
                                     csq_cmd.QSIZE + 1,
                                     NVMeDeviceCommon.sq_entry_size,
                                     csq_cmd.QID,
                                     (ctypes.addressof(
                                         nvsim_state.nvme_regs.SQNDBS[0]) +
                                         ((csq_cmd.QID * 8))))
        # Find the associated CQ
        cqs = [c for c in nvsim_state.completion_queues if c.qid == csq_cmd.CQID]
        if len(cqs) == 0:
            self.complete(command, sq, cq, status_codes['Invalid Field in Command'])
            return

        # Add it to the list
        nvsim_state.queue_mgr.add(new_sq, cqs[0])
        self.complete(command, sq, cq, status_codes['Successful Completion'])


class NVSimFormat:
    OPC = FormatNVM().OPC

    def __call__(self, nvsim_state, command, sq, cq):
        fmt_cmd = FormatNVM.from_buffer(command)

        # Re-initialize our backend storage
        nvsim_state.namespaces[fmt_cmd.NSID].init_storage()

        self.complete(command, sq, cq, status_codes['Successful Completion'])


# Create our admin command handlers object. Can you do this with introspection??
admin_handlers = NvsimCommandHandlers()
for handler in [
    NVSimIdentify,
    NVSimCreateIOCompletionQueue,
    NVSimCreateIOSubmissionQueue,
    NVSimFormat,
]:
    admin_handlers.register(handler)
