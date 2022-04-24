import ctypes
from stdk.nvme.spec.structures import ADMINCommand, ADMINStatusValue


class CreateIOSubmissionQueue(ADMINCommand):
    completion_status = [
        ADMINStatusValue('COMPLETION_QUEUE_INVALID', 0x00),
        ADMINStatusValue('INVALID_QUEUE_IDENTIFIER', 0x01),
        ADMINStatusValue('INVALID_QUEUE_SIZE', 0x02),
    ]

    _fields_ = [
        ('QID', ctypes.c_uint32, 16),
        ('QSIZE', ctypes.c_uint32, 16),

        ('PC', ctypes.c_uint32, 1),
        ('QPRIO', ctypes.c_uint32, 2),
        ('RSVD_0', ctypes.c_uint32, 13),
        ('CQID', ctypes.c_uint32, 16),

        ('NVMSETID', ctypes.c_uint32, 16),
        ('RSVD_2', ctypes.c_uint32, 16),
    ]

    _defaults_ = {
        'OPC': 0x01
    }
    data_out = None
    data_in = None
