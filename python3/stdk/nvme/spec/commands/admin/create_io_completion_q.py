import ctypes
from stdk.nvme.spec.structures import ADMINCommand, ADMINStatusValue


class CreateIOCompletionQueue(ADMINCommand):
    completion_status = [
        ADMINStatusValue('INVALID_QUEUE_IDENTIFIER', 0x01),
        ADMINStatusValue('INVALID_QUEUE_SIZE', 0x02),
        ADMINStatusValue('INVALID_INTERRUPT_VECTOR', 0x08),
    ]

    _fields_ = [
        ('QID', ctypes.c_uint32, 16),
        ('QSIZE', ctypes.c_uint32, 16),

        ('PC', ctypes.c_uint32, 1),
        ('IEN', ctypes.c_uint32, 1),
        ('RSVD_0', ctypes.c_uint32, 14),
        ('IV', ctypes.c_uint32, 16),
    ]

    _defaults_ = {
        'OPC': 0x05
    }
    data_out = None
    data_in = None
