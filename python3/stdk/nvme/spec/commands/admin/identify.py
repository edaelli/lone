import ctypes
from stdk.nvme.spec.structures import ADMINCommand, DataInCommon


class IdentifyData(DataInCommon):
    size = 4096
    _fields_ = [
        ('DATA', ctypes.c_uint8 * size),
    ]


class Identify(ADMINCommand):
    _fields_ = [
        ('CNS', ctypes.c_uint32, 8),
        ('RSVD_0', ctypes.c_uint32, 8),
        ('CNTID', ctypes.c_uint32, 16),

        ('NVMSETID', ctypes.c_uint32, 16),
        ('RSVD_1', ctypes.c_uint32, 16),

        ('DW12', ctypes.c_uint32),
        ('DW13', ctypes.c_uint32),

        ('UUID', ctypes.c_uint32, 7),
        ('RSVD_2', ctypes.c_uint32, 25),

        ('DW15', ctypes.c_uint32),
    ]
    _defaults_ = {
        'OPC': 0x06
    }
    data_out = None
    data_in = IdentifyData()


class IdentifyNamespaceData(DataInCommon):
    size = 4096

    class LBAFormat(ctypes.Structure):
        _pack_ = 1
        size = 4
        _fields_ = [
            ('MS', ctypes.c_uint32, 16),
            ('LBADS', ctypes.c_uint32, 8),
            ('RP', ctypes.c_uint32, 2),
            ('RSVD', ctypes.c_uint32, 6),
        ]

    _fields_ = [
        ('NSZE', ctypes.c_uint64),
        ('NCAP', ctypes.c_uint64),
        ('NUSE', ctypes.c_uint64),
        ('NSFEAT', ctypes.c_uint8),
        ('NLBAF', ctypes.c_uint8),
        ('FLBAS', ctypes.c_uint8),
        ('MC', ctypes.c_uint8),
        ('DPC', ctypes.c_uint8),
        ('DPS', ctypes.c_uint8),
        ('NMIC', ctypes.c_uint8),
        ('RESCAP', ctypes.c_uint8),
        ('FPI', ctypes.c_uint8),
        ('DLFEAT', ctypes.c_uint8),
        ('NAWUN', ctypes.c_uint16),
        ('RSVD_0', ctypes.c_uint8 * 92),
        ('LBAF_TBL', LBAFormat * 16),
        ('RSVD_1', ctypes.c_uint8 * 3904),
    ]


class IdentifyNamespace(Identify):
    _defaults_ = {
        'OPC': 0x06,
        'CNS': 0x00
    }
    data_out = None
    data_in = IdentifyNamespaceData()


class IdentifyControllerData(DataInCommon):
    size = 4096
    _fields_ = [
        ('VID', ctypes.c_uint16),
        ('SSVID', ctypes.c_uint16),
        ('SN', ctypes.c_char * 20),
        ('MN', ctypes.c_char * 40),
        ('FR', ctypes.c_char * 8),
        ('RAB', ctypes.c_uint8),
        ('IEEE', ctypes.c_uint8 * 3),
        ('CMIC', ctypes.c_uint8),
        ('MDTS', ctypes.c_uint8),
        ('CNTLID', ctypes.c_uint16),
        ('VER', ctypes.c_uint32),
        ('RTD3R', ctypes.c_uint32),
        ('RTD3E', ctypes.c_uint32),
        ('OAES', ctypes.c_uint32),
        ('CTRATT', ctypes.c_uint32),
        ('RRLS', ctypes.c_uint16),
        ('RSVD_0', ctypes.c_uint8 * 9),
        ('CNTRLTYPE', ctypes.c_uint8),
        ('FGUID', ctypes.c_uint8 * 16),
        ('TBD_0', ctypes.c_uint8 * 388),
        ('NN', ctypes.c_uint32),
        ('TBD_1', ctypes.c_uint8 * 3576),
    ]


class IdentifyController(Identify):
    _defaults_ = {
        'OPC': 0x06,
        'CNS': 0x01
    }
    data_out = None
    data_in = IdentifyControllerData()


class IdentifyNamespaceListData(DataInCommon):
    size = 4096
    _fields_ = [
        ('Identifiers', ctypes.c_uint32 * 1024),
    ]


class IdentifyNamespaceList(Identify):
    _defaults_ = {
        'OPC': 0x06,
        'CNS': 0x02
    }
    data_out = None
    data_in = IdentifyNamespaceListData()
