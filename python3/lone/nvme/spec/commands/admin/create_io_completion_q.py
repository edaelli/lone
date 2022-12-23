import ctypes
from lone.nvme.spec.structures import ADMINCommand
from lone.nvme.spec.commands.status_codes import NVMeStatusCode, status_codes


class CreateIOCompletionQueue(ADMINCommand):
    _pack_ = 1
    _fields_ = [
        ('QID', ctypes.c_uint32, 16),
        ('QSIZE', ctypes.c_uint32, 16),

        ('PC', ctypes.c_uint32, 1),
        ('IEN', ctypes.c_uint32, 1),
        ('RSVD_0', ctypes.c_uint32, 14),
        ('IV', ctypes.c_uint32, 16),

        ('DW12', ctypes.c_uint32),
        ('DW13', ctypes.c_uint32),
        ('DW14', ctypes.c_uint32),
        ('DW15', ctypes.c_uint32),
    ]

    _defaults_ = {
        'OPC': 0x05
    }


status_codes.add([
    NVMeStatusCode(0x01, 'Invalid Queue Identifier', CreateIOCompletionQueue),
    NVMeStatusCode(0x02, 'Invalid Queue Size', CreateIOCompletionQueue),
    NVMeStatusCode(0x03, 'Invalid Interrupt Vector', CreateIOCompletionQueue),
])
