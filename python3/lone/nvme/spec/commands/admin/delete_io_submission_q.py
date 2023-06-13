import ctypes
from lone.nvme.spec.structures import ADMINCommand
from lone.nvme.spec.commands.status_codes import NVMeStatusCode, status_codes


class DeleteIOSubmissionQueue(ADMINCommand):
    _pack_ = 1
    _fields_ = [
        ('QID', ctypes.c_uint32, 16),
        ('RSVD_0', ctypes.c_uint32, 16),

        ('DW11', ctypes.c_uint32),
        ('DW12', ctypes.c_uint32),
        ('DW13', ctypes.c_uint32),
        ('DW14', ctypes.c_uint32),
        ('DW15', ctypes.c_uint32),
    ]

    _defaults_ = {
        'OPC': 0x00
    }


status_codes.add([
    NVMeStatusCode(0x01, 'Invalid Queue Identifier', DeleteIOSubmissionQueue),
])
