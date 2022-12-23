from lone.nvme.spec.structures import CQE

import logging
logger = logging.getLogger('nvsim_cmd_h')


class NvsimCommandHandlers:
    def __init__(self):
        self.handlers = {}

    def register(self, handler):
        assert handler.OPC not in self.handlers, (
            'OPC: 0x{:x} already in the list of handlers!'.format(handler.OPC))
        self.handlers[handler.OPC] = handler()
        handler.complete = NvsimCommandHandler.complete


class NvsimCommandHandler:

    def complete(self, command, sq, cq, status_code):
        # Complete the command
        cqe = CQE()
        cqe.CID = command.CID
        cqe.SF.SC = int(status_code)
        cqe.SQID = sq.qid
        cqe.SQHD = sq.head.value
        cq.post_completion(cqe)

        if status_code.failure:
            logger.info('Command OPC 0x{:x} resulted in "{}"'.format(command.OPC, status_code))
