import ctypes
from stdk.nvme.spec.structures import NVMCommand, NVMStatusValue


class Read(NVMCommand):
    completion_status = [
        NVMStatusValue('CONFLICTING_ATTRIBUTES', 0x80),
        NVMStatusValue('INVALID_PROTECTION_INFORMATION', 0x81),
    ]

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
        ('RSVD_0', ctypes.c_uint32, 8),
        ('STC', ctypes.c_uint32, 1),
        ('RSVD_1', ctypes.c_uint32, 1),
        ('PRINFO', ctypes.c_uint32, 4),
        ('FUA', ctypes.c_uint32, 1),
        ('LR', ctypes.c_uint32, 1),

        ('DSM', Dsm),
        ('RSVD_1', ctypes.c_uint8),
        ('RSVD_2', ctypes.c_uint16),

        ('ELBST_EILBRT', ctypes.c_uint32),

        ('ELBAT', ctypes.c_uint32, 16),
        ('ELBATM', ctypes.c_uint32, 16),
    ]

    _defaults_ = {
        'OPC': 0x02
    }
