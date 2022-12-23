import ctypes
from lone.nvme.spec.structures import NVMCommand
from lone.nvme.spec.commands.status_codes import NVMeStatusCode, status_codes


class Write(NVMCommand):
    _pack_ = 1

    class Dsm(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('AF', ctypes.c_uint8, 4),
            ('AL', ctypes.c_uint8, 2),
            ('SR', ctypes.c_uint8, 1),
            ('I', ctypes.c_uint8, 1),
        ]

    _fields_ = [
        ('SLBA', ctypes.c_uint64),

        ('NLB', ctypes.c_uint32, 16),
        ('RSVD_0', ctypes.c_uint32, 4),
        ('DTYPE', ctypes.c_uint32, 4),
        ('STC', ctypes.c_uint32, 1),
        ('RSVD_1', ctypes.c_uint32, 1),
        ('PRINFO', ctypes.c_uint32, 4),
        ('FUA', ctypes.c_uint32, 1),
        ('LR', ctypes.c_uint32, 1),

        ('DSM', Dsm),
        ('RSVD_2', ctypes.c_uint8),
        ('DSPEC', ctypes.c_uint16),

        ('ELBST_EILBRT', ctypes.c_uint32),

        ('LBAT', ctypes.c_uint32, 16),
        ('LBATM', ctypes.c_uint32, 16),
    ]

    _defaults_ = {
        'OPC': 0x01
    }


status_codes.add([
    NVMeStatusCode(0x20, 'Namespace Write Protected', Write),
    NVMeStatusCode(0x80, 'Conflicting Attributes', Write),
    NVMeStatusCode(0x81, 'Invalid Protection Information', Write),
    NVMeStatusCode(0x82, 'Attempted Write to Read Only Range', Write),
])
