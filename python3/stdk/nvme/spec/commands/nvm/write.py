import ctypes
from stdk.nvme.spec.structures import NVMCommand, NVMStatusValue


class Write(NVMCommand):
    completion_status = [
        NVMStatusValue('NAMESPACE_WRITE_PROTECTED', 0x20),
        NVMStatusValue('CONFLICTING_ATTRIBUTES', 0x80),
        NVMStatusValue('INVALID_PROTECTION_INFORMATION', 0x81),
        NVMStatusValue('ATTEMPTED_WRITE_TO_READ_ONLY_RANGE', 0x82),
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
        ('RSVD_0', ctypes.c_uint32, 4),
        ('DTYPE', ctypes.c_uint32, 4),
        ('STC', ctypes.c_uint32, 1),
        ('RSVD_1', ctypes.c_uint32, 1),
        ('PRINFO', ctypes.c_uint32, 4),
        ('FUA', ctypes.c_uint32, 1),
        ('LR', ctypes.c_uint32, 1),

        ('DSM', Dsm),
        ('RSVD_2', ctypes.c_uint8),
        ('DSPEC', ctypes.c_uint32, 16),

        ('ELBST_EILBRT', ctypes.c_uint32),

        ('LBAT', ctypes.c_uint32, 16),
        ('LBATM', ctypes.c_uint32, 16),
    ]

    _defaults_ = {
        'OPC': 0x01
    }
