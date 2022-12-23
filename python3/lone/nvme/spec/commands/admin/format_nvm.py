import ctypes
from lone.nvme.spec.structures import ADMINCommand
from lone.nvme.spec.commands.status_codes import NVMeStatusCode, status_codes


class FormatNVM(ADMINCommand):
    _pack_ = 1
    _fields_ = [
        ('LBAFL', ctypes.c_uint32, 4),
        ('MSET', ctypes.c_uint32, 1),
        ('PI', ctypes.c_uint32, 3),
        ('PIL', ctypes.c_uint32, 1),
        ('SES', ctypes.c_uint32, 3),
        ('LBAFU', ctypes.c_uint32, 2),
        ('RSVD_0', ctypes.c_uint32, 18),

        ('DW11', ctypes.c_uint32),
        ('DW12', ctypes.c_uint32),
        ('DW13', ctypes.c_uint32),
        ('DW14', ctypes.c_uint32),
        ('DW15', ctypes.c_uint32),
    ]

    _defaults_ = {
        'OPC': 0x80
    }


status_codes.add([
    NVMeStatusCode(0x0A, 'Invalid Format', FormatNVM),
    NVMeStatusCode(0x0C, 'Command Seequence Error', FormatNVM),
    NVMeStatusCode(0x15, 'Operation Denied', FormatNVM),
    NVMeStatusCode(0x20, 'Namespace Write Protected', FormatNVM),
    NVMeStatusCode(0x86, 'Access Denied', FormatNVM),
])
