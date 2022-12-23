import ctypes
from lone.nvme.spec.structures import ADMINCommand, DataInCommon


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

        ('CNSSPEC', ctypes.c_uint32, 16),
        ('RSVD_1', ctypes.c_uint32, 8),
        ('CSI', ctypes.c_uint32, 8),

        ('DW12', ctypes.c_uint32),
        ('DW13', ctypes.c_uint32),

        ('UUID', ctypes.c_uint32, 7),
        ('RSVD_2', ctypes.c_uint32, 25),

        ('DW15', ctypes.c_uint32),
    ]
    _defaults_ = {
        'OPC': 0x06
    }
    data_in_type = IdentifyData


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
    data_in_type = IdentifyNamespaceData


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
        'CNS': 0x01,
    }
    data_in_type = IdentifyControllerData


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
    data_in_type = IdentifyNamespaceListData


class IdentifyUUIDListData(DataInCommon):
    size = 4096

    class IdentifyUUIDEntry(ctypes.Structure):
        _pack_ = 1
        size = 32
        _fields_ = [
            ('IdAss', ctypes.c_uint8, 2),
            ('RSVD_0', ctypes.c_uint8, 6),

            ('RSVD_1', ctypes.c_uint8 * 15),

            ('UUID', ctypes.c_uint8 * 16),
        ]

    _fields_ = [
        ('UUIDS', IdentifyUUIDEntry * 128),
    ]


class IdentifyUUIDList(Identify):
    _defaults_ = {
        'OPC': 0x06,
        'CNS': 0x17
    }
    data_in_type = IdentifyUUIDListData


class IdentifyNamespaceZonedData(DataInCommon):
    size = 4096

    class LBAFormatExtended(ctypes.Structure):
        _pack_ = 1
        size = 128
        _fields_ = [
            ('ZSZE', ctypes.c_uint64),
            ('ZDES', ctypes.c_uint8),
            ('RSVD_0)', ctypes.c_uint8 * 56),
        ]

    _fields_ = [
        ('ZOC', ctypes.c_uint16),
        ('OZCS', ctypes.c_uint16),
        ('MAR', ctypes.c_uint32),
        ('MOR', ctypes.c_uint32),
        ('RRL', ctypes.c_uint32),
        ('FRL', ctypes.c_uint32),
        ('RRL1', ctypes.c_uint32),
        ('RRL2', ctypes.c_uint32),
        ('RRL3', ctypes.c_uint32),
        ('FRL1', ctypes.c_uint32),
        ('FRL2', ctypes.c_uint32),
        ('FRL3', ctypes.c_uint32),
        ('RSVD_0', ctypes.c_uint8 * 2772),
        ('LBAFE_TBL', LBAFormatExtended * 64),
        ('RSVD_1)', ctypes.c_uint8 * 256),
    ]


class IdentifyNamespaceZoned(Identify):
    _defaults_ = {
        'OPC': 0x06,
        'CNS': 0x05,
        'CSI': 0x02,
    }
    data_in_type = IdentifyNamespaceZonedData


class IdentifyIoCmdSetData(DataInCommon):
    size = 4096

    class IoCmdSetVector(ctypes.Structure):
        _pack_ = 1
        size = 64
        _fields_ = [
            ('NVMCmdSet', ctypes.c_uint64, 1),
            ('KeyValueCmdSet', ctypes.c_uint64, 1),
            ('ZonedNamespaceCmdSet', ctypes.c_uint64, 1),
            ('Reserved', ctypes.c_uint64, 61),
        ]

    _fields_ = [
        ('IoCmdSetVectors', IoCmdSetVector * 512),
    ]


class IdentifyIoCmdSet(Identify):
    _defaults_ = {
        'OPC': 0x06,
        'CNS': 0x1C,
    }
    data_in_type = IdentifyIoCmdSetData
