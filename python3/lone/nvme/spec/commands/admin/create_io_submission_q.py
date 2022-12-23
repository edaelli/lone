import ctypes
from lone.nvme.spec.structures import ADMINCommand
from lone.nvme.spec.commands.status_codes import NVMeStatusCode, status_codes


class CreateIOSubmissionQueue(ADMINCommand):
    _pack_ = 1
    _fields_ = [
        ('QID', ctypes.c_uint32, 16),
        ('QSIZE', ctypes.c_uint32, 16),

        ('PC', ctypes.c_uint32, 1),
        ('QPRIO', ctypes.c_uint32, 2),
        ('RSVD_0', ctypes.c_uint32, 13),
        ('CQID', ctypes.c_uint32, 16),

        ('NVMSETID', ctypes.c_uint32, 16),
        ('RSVD_2', ctypes.c_uint32, 16),

        ('DW13', ctypes.c_uint32),
        ('DW14', ctypes.c_uint32),
        ('DW15', ctypes.c_uint32),
    ]

    _defaults_ = {
        'OPC': 0x01
    }


status_codes.add([
    NVMeStatusCode(0x00, 'Completion Queue Invalid', CreateIOSubmissionQueue),
    NVMeStatusCode(0x01, 'Invalid Queue Identifier', CreateIOSubmissionQueue),
    NVMeStatusCode(0x02, 'Invalid Queue Size', CreateIOSubmissionQueue),
])
