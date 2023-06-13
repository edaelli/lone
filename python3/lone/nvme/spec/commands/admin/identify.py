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

    class PowerStateDesc(ctypes.Structure):
        _pack_ = 1
        size = 32
        _fields_ = [
            ('MP', ctypes.c_uint16),
            ('RSVD_0', ctypes.c_uint8),
            ('MXPS', ctypes.c_uint8, 1),
            ('NOPS', ctypes.c_uint8, 1),
            ('RSVD_1', ctypes.c_uint8, 6),

            ('ENLAT', ctypes.c_uint32),

            ('EXLAT', ctypes.c_uint32),

            ('RRT', ctypes.c_uint32, 5),
            ('RSVD_2', ctypes.c_uint32, 3),
            ('RRL', ctypes.c_uint32, 5),
            ('RSVD_3', ctypes.c_uint32, 3),
            ('RWT', ctypes.c_uint32, 5),
            ('RSVD_4', ctypes.c_uint32, 3),
            ('RWL', ctypes.c_uint32, 5),
            ('RSVD_5', ctypes.c_uint32, 3),

            ('IDLP', ctypes.c_uint32, 16),
            ('RSVD_6', ctypes.c_uint32, 6),
            ('IPS', ctypes.c_uint32, 2),
            ('RSVD_7', ctypes.c_uint32, 8),

            ('ACTP', ctypes.c_uint32, 16),
            ('APW', ctypes.c_uint32, 3),
            ('RSVD_8', ctypes.c_uint32, 3),
            ('APS', ctypes.c_uint32, 2),
            ('RSVD_9', ctypes.c_uint32, 8),

            ('RSVD_10', ctypes.c_uint8 * 8),
        ]

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
        ('CRDT1', ctypes.c_uint16),
        ('CRDT2', ctypes.c_uint16),
        ('CRDT3', ctypes.c_uint16),
        ('RSVD_1', ctypes.c_uint8 * 119),
        ('NVMSR', ctypes.c_uint8),
        ('VWCI', ctypes.c_uint8),
        ('MEC', ctypes.c_uint8),
        ('OACS', ctypes.c_uint16),
        ('ACL', ctypes.c_uint8),
        ('AERL', ctypes.c_uint8),
        ('FRMW', ctypes.c_uint8),
        ('LPA', ctypes.c_uint8),
        ('ELPE', ctypes.c_uint8),
        ('NPSS', ctypes.c_uint8),
        ('AVSCC', ctypes.c_uint8),
        ('APSTA', ctypes.c_uint8),
        ('WCTEMP', ctypes.c_uint16),
        ('CCTEMP', ctypes.c_uint16),
        ('MTFA', ctypes.c_uint16),
        ('HMPRE', ctypes.c_uint32),
        ('HMMIN', ctypes.c_uint32),
        ('TNVMCAP_LO', ctypes.c_uint64),
        ('TNVMCAP_HI', ctypes.c_uint64),
        ('UNVMCAP_LO', ctypes.c_uint64),
        ('UNVMCAP_HI', ctypes.c_uint64),
        ('RPMBS', ctypes.c_uint32),
        ('EDSTT', ctypes.c_uint16),
        ('DSTO', ctypes.c_uint8),
        ('FWUG', ctypes.c_uint8),
        ('KAS', ctypes.c_uint16),
        ('HCTMA', ctypes.c_uint16),
        ('MNTMT', ctypes.c_uint16),
        ('MXTMT', ctypes.c_uint16),
        ('SANICAP', ctypes.c_uint32),
        ('HMMINDS', ctypes.c_uint32),
        ('HMMAXD', ctypes.c_uint16),
        ('NSETIDMAX', ctypes.c_uint16),
        ('ENDGIDMAX', ctypes.c_uint16),
        ('ANATT', ctypes.c_uint8),
        ('ANACAP', ctypes.c_uint8),
        ('ANAGRPMAX', ctypes.c_uint32),
        ('NANAGRPID', ctypes.c_uint32),
        ('PELS', ctypes.c_uint32),
        ('DOMID', ctypes.c_uint16),
        ('RSVD_2', ctypes.c_uint8 * 10),
        ('MEGCAP_LO', ctypes.c_uint64),
        ('MEGCAP_HI', ctypes.c_uint64),
        ('RSVD_3', ctypes.c_uint8 * 128),
        ('SQES', ctypes.c_uint8),
        ('CQES', ctypes.c_uint8),
        ('MAXCMD', ctypes.c_uint16),
        ('NN', ctypes.c_uint32),
        ('ONCS', ctypes.c_uint16),
        ('FUSES', ctypes.c_uint16),
        ('FNA', ctypes.c_uint8),
        ('VWC', ctypes.c_uint8),
        ('AWUN', ctypes.c_uint16),
        ('AWUPF', ctypes.c_uint16),
        ('ICSVSCC', ctypes.c_uint8),
        ('NWPC', ctypes.c_uint8),
        ('ACWU', ctypes.c_uint16),
        ('CPFMTSUP', ctypes.c_uint16),
        ('SGLS', ctypes.c_uint32),
        ('MNAN', ctypes.c_uint32),
        ('MAXDNA_LO', ctypes.c_uint64),
        ('MAXDNA_HI', ctypes.c_uint64),
        ('MAXCNA', ctypes.c_uint32),
        ('RSVD_4', ctypes.c_uint8 * 204),
        ('SUBNQN', ctypes.c_char * 256),
        ('RSVD_5', ctypes.c_uint8 * 768),
        ('IOCCSZ', ctypes.c_uint32),
        ('IORCSZ', ctypes.c_uint32),
        ('ICDOFF', ctypes.c_uint16),
        ('FCATT', ctypes.c_uint8),
        ('MSDBD', ctypes.c_uint8),
        ('OFCS', ctypes.c_uint16),
        ('RSVD_6', ctypes.c_uint8 * 242),
        ('PSDS', PowerStateDesc * 32),
        ('VS', ctypes.c_uint8 * 1024),
    ]


# Check size and a few offsets to make sure they match the spec
assert ctypes.sizeof(IdentifyControllerData) == IdentifyControllerData.size
assert IdentifyControllerData.VS.offset == 3072
assert IdentifyControllerData.MAXCNA.offset == 560
assert IdentifyControllerData.ONCS.offset == 520
assert IdentifyControllerData.CCTEMP.offset == 268
assert IdentifyControllerData.IEEE.offset == 73


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
        ('RSVD_1', ctypes.c_uint8 * 256),
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
