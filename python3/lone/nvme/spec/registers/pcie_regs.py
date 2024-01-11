import ctypes
import logging
from collections import namedtuple

from lone.util.struct_tools import StructFieldsIterator
from lone.nvme.spec.registers import RegsStructAccess


#   pci registers in various implementations.
PCIeAccessData = namedtuple('PCIeAccessData', 'get_func set_func')


def pcie_reg_struct_factory(access_data):

    class NVMePCIeRegisters(ctypes.Structure):

        class Id(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('VID', ctypes.c_uint32, 16),
                ('DID', ctypes.c_uint32, 16),
            ]
            _access_ = access_data
            _base_offset_ = 0x00

        class Cmd(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('IOSE', ctypes.c_uint16, 1),
                ('MSE', ctypes.c_uint16, 1),
                ('BME', ctypes.c_uint16, 1),
                ('SCE', ctypes.c_uint16, 1),
                ('MWIE', ctypes.c_uint16, 1),
                ('VGA', ctypes.c_uint16, 1),
                ('PEE', ctypes.c_uint16, 1),
                ('RSVD_0', ctypes.c_uint16, 1),
                ('SEE', ctypes.c_uint16, 1),
                ('FBE', ctypes.c_uint16, 1),
                ('ID', ctypes.c_uint16, 1),
                ('RSVD_1', ctypes.c_uint16, 5),
            ]
            _access_ = access_data
            _base_offset_ = 0x04

        class Sts(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('RSVD_0', ctypes.c_uint16, 3),
                ('IS', ctypes.c_uint16, 1),
                ('CL', ctypes.c_uint16, 1),
                ('C66', ctypes.c_uint16, 1),
                ('RSVD_1', ctypes.c_uint16, 1),
                ('FBC', ctypes.c_uint16, 1),
                ('DPD', ctypes.c_uint16, 1),
                ('DEVT', ctypes.c_uint16, 2),
                ('STA', ctypes.c_uint16, 1),
                ('RTA', ctypes.c_uint16, 1),
                ('RMA', ctypes.c_uint16, 1),
                ('SSE', ctypes.c_uint16, 1),
                ('DPE', ctypes.c_uint16, 1),
            ]
            _access_ = access_data
            _base_offset_ = 0x06

        class Rid(RegsStructAccess):
            _pack = 1
            _fields_ = [
                ('RID', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x08

        class Cc(RegsStructAccess):
            _pack = 1
            _fields_ = [
                ('PI', ctypes.c_uint8),
                ('SCC', ctypes.c_uint8),
                ('BCC', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x09

        class Cls(RegsStructAccess):
            _pack = 1
            _fields_ = [
                ('CLS', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x0C

        class Mlt(RegsStructAccess):
            _pack = 1
            _fields_ = [
                ('MLT', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x0D

        class Htype(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('HL', ctypes.c_uint8, 7),
                ('MFD', ctypes.c_uint8, 1),
            ]
            _access_ = access_data
            _base_offset_ = 0x0E

        class Bist(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('CC', ctypes.c_uint8, 4),
                ('RSVD_1', ctypes.c_uint8, 2),
                ('SB', ctypes.c_uint8, 1),
                ('BC', ctypes.c_uint8, 1),
            ]
            _access_ = access_data
            _base_offset_ = 0x0F

        class Bar0(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('RTE', ctypes.c_uint32, 1),
                ('TP', ctypes.c_uint32, 2),
                ('PF', ctypes.c_uint32, 1),
                ('RSVD_1', ctypes.c_uint32, 10),
                ('BA', ctypes.c_uint32, 18),
            ]
            _access_ = access_data
            _base_offset_ = 0x10

        class Bar1(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('BA', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x14

        class Bar2(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('RTE', ctypes.c_uint32, 1),
                ('RSVD_1', ctypes.c_uint32, 13),
                ('BA', ctypes.c_uint32, 18),
            ]
            _access_ = access_data
            _base_offset_ = 0x18

        class Bar3(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('VU', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x1C

        class Bar4(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('VU', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x20

        class Bar5(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('VU', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x24

        class Ccptr(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('NOT_SUPPORTED', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x28

        class Ss(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('SSVID', ctypes.c_uint16),
                ('SSID', ctypes.c_uint16),
            ]
            _access_ = access_data
            _base_offset_ = 0x2C

        class Erom(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('RBA', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x30

        class Cap(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('CP', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x34

        class Intr(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('ILINE', ctypes.c_uint8),
                ('IPIN', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x3C

        class Mgnt(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('GNT', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x3E

        class Mlat(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('LAT', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x3F

        class Caps(RegsStructAccess):
            _pack_ = 1
            _fields_ = [
                ('DATA', ctypes.c_uint8 * 4032),
            ]
            _access_ = access_data
            _base_offset_ = 0x40

        ''' PCIe registers from the NVMe specification
        '''
        _pack_ = 1
        _fields_ = [
            ('ID', Id),
            ('CMD', Cmd),
            ('STS', Sts),
            ('RID', Rid),
            ('CC', Cc),
            ('CLS', Cls),
            ('MLT', Mlt),
            ('HTYPE', Htype),
            ('BIST', Bist),
            ('BAR0', Bar0),
            ('BAR1', Bar1),
            ('BAR2', Bar2),
            ('BAR3', Bar3),
            ('BAR4', Bar4),
            ('BAR5', Bar5),
            ('CCPTR', Ccptr),
            ('SS', Ss),
            ('EROM', Erom),
            ('CAP', Cap),
            ('RSVD_0', ctypes.c_uint8 * 5),
            ('RSVD_1', ctypes.c_uint16),
            ('INTR', Intr),
            ('MGNT', Mgnt),
            ('MLAT', Mlat),
            ('CAPS', Caps),
        ]
        _access_ = access_data
        _base_offset_ = 0x00

    return NVMePCIeRegisters


class PCIeRegisters:

    def init_capabilities(self):
        self.capabilities = []

        # Get the pointer to the first capability and walk the list saving each in
        #  the self.capabilities list
        next_cap_ptr = self.CAP.CP
        while next_cap_ptr:
            # Create a generic capability object to figure out its type
            cap_gen = PCICapabilityGen(self, next_cap_ptr)
            cap_obj = PCICapabilityIdTable.ids[cap_gen.CAP_ID]
            # if cap_obj == PCICapabilityGen:
            # print('Unknown Capability ID: 0x{:02x}'.format(cap_gen.CAP_ID))

            # Now that we know the type, create the real object and add to the array
            capability = cap_obj(self, next_cap_ptr)
            self.capabilities.append(capability)

            # Advance next pointer
            next_cap_ptr = capability.NEXT_PTR

        # Same thing for extended capabilities
        next_cap_ptr = 0x100
        while next_cap_ptr:
            # Create a generic capability object to figure out its type
            cap_gen = PCICapabilityGen(self, next_cap_ptr)
            cap_obj = PCICapabilityExtendedIdTable.ids[cap_gen.CAP_ID]
            # if cap_obj == PCICapabilityGenExtended:
            # print('Unknown Extended Capability ID: 0x{:02x}'.format(cap_gen.CAP_ID))

            # Now that we know the type, create the real object and add to the array
            capability = cap_obj(self, next_cap_ptr)
            self.capabilities.append(capability)

            # Advance next pointer
            next_cap_ptr = capability.NEXT_PTR

    def log(self):
        log = logging.getLogger('pcie_regs')
        for field, value in StructFieldsIterator(self):
            if 'RSVD' not in field:
                log.debug('{:50} 0x{:x}'.format(field, value))
                print('{:50} 0x{:x}'.format(field, value))


class PCIeRegistersDirect(pcie_reg_struct_factory(PCIeAccessData(None, None)), PCIeRegisters):
    pass


class PCICapability(ctypes.Structure):
    def __init__(self, registers, offset):
        self.registers = registers
        self.offset = offset

    def read_bytes(self):
        start_byte = self.offset - type(self.registers).CAPS.offset
        end_byte = start_byte + ctypes.sizeof(self)
        cap_bytes = bytearray(self.registers.CAPS.DATA[start_byte:end_byte])

        class CapStructure(ctypes.Structure):
            _fields_ = self._fields_

        cap_copy = CapStructure.from_buffer(cap_bytes)
        return cap_copy

    def __getattribute__(self, name):
        if name in [f[0] for f in object.__getattribute__(self, '_fields_')]:
            cap = self.read_bytes()
            return getattr(cap, name)
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in [f[0] for f in object.__getattribute__(self, '_fields_')]:
            write_bytes = bytes(value)
            byte_offset = getattr(type(self), name).offset
            start_byte = self.offset - type(self.registers).CAPS.offset + byte_offset
            data = self.registers.CAPS.DATA
            for i in range(len(write_bytes)):
                data[start_byte + i] = write_bytes[i]
            self.registers.CAPS.DATA = data

        else:
            return object.__setattr__(self, name, value)

    def log(self):
        log = logging.getLogger('capability')

        log.debug('\n')
        log.debug('{}: next 0x{:x}'.format(
                  self.__class__.__name__, self.NEXT_PTR))

        for field, value in StructFieldsIterator(self):
            if 'RSVD' not in field:
                log.debug('{:50} 0x{:x}'.format(field, value))
                print('{:50} 0x{:x}'.format(field, value))


class PCICapabilityGen(PCICapability):
    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint8),
        ('NEXT_PTR', ctypes.c_uint8),
        ('CAP_REG', ctypes.c_uint16),
    ]


class PCICapPowerManagementInterface(PCICapability):
    _cap_id_ = 0x1

    class Pc(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('VS', ctypes.c_uint16, 3),
            ('PMEC', ctypes.c_uint16, 1),
            ('RSVD_0', ctypes.c_uint16, 1),
            ('DSI', ctypes.c_uint16, 1),
            ('AUXC', ctypes.c_uint16, 3),
            ('D1S', ctypes.c_uint16, 1),
            ('D2S', ctypes.c_uint16, 1),
            ('PSUP', ctypes.c_uint16, 5),
        ]

    class Pmcs(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('PS', ctypes.c_uint16, 2),
            ('RSVD_0', ctypes.c_uint16, 1),
            ('NSFRST', ctypes.c_uint16, 1),
            ('RSVD_1', ctypes.c_uint16, 4),
            ('PMEE', ctypes.c_uint16, 1),
            ('DSE', ctypes.c_uint16, 4),
            ('DSC', ctypes.c_uint16, 2),
            ('PMES', ctypes.c_uint16, 1),
        ]

    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint8),
        ('NEXT_PTR', ctypes.c_uint8),
        ('PC', Pc),
        ('PMCS', Pmcs),
    ]


class PCICapMSI(PCICapability):
    _cap_id_ = 0x05

    class Mc(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('MSIE', ctypes.c_uint16, 1),
            ('MMC', ctypes.c_uint16, 3),
            ('MME', ctypes.c_uint16, 3),
            ('C64', ctypes.c_uint16, 1),
            ('PVM', ctypes.c_uint16, 1),
            ('RSVD_0', ctypes.c_uint16, 7),
        ]

    class Ma(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint32, 2),
            ('ADDR', ctypes.c_uint32, 30),
        ]

    class Mua(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('UADDR', ctypes.c_uint32),
        ]

    class Md(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('DATA', ctypes.c_uint16),
        ]

    class Mmask(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('MASK', ctypes.c_uint32),
        ]

    class Mpend(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('PEND', ctypes.c_uint32),
        ]

    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint8),
        ('NEXT_PTR', ctypes.c_uint8),
        ('MC', Mc),
        ('MA', Ma),
        ('MUA', Mua),
        ('MD', Md),
        ('MMASK', Mmask),
        ('MPEND', Mpend),
    ]


class PCICapMSIX(PCICapability):
    _cap_id_ = 0x11

    class Mxc(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('TS', ctypes.c_uint16, 11),
            ('RSVD_0', ctypes.c_uint16, 3),
            ('FM', ctypes.c_uint16, 1),
            ('MXE', ctypes.c_uint16, 1),
        ]

    class Mtab(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('TBIR', ctypes.c_uint32, 3),
            ('TO', ctypes.c_uint32, 29),
        ]

    class Mpba(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('PBIR', ctypes.c_uint32, 3),
            ('PBAO', ctypes.c_uint32, 29),
        ]

    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint8),
        ('NEXT_PTR', ctypes.c_uint8),
        ('MXC', Mxc),
        ('MTAB', Mtab),
        ('MPBA', Mpba),
    ]


class PCICapExpress(PCICapability):
    _cap_id_ = 0x10

    class Pxcap(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('VER', ctypes.c_uint16, 4),
            ('DPT', ctypes.c_uint16, 4),
            ('SI', ctypes.c_uint16, 1),
            ('IMN', ctypes.c_uint16, 5),
            ('RSVD_0', ctypes.c_uint16, 2),
        ]

    class Pxdcap(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('MPS', ctypes.c_uint32, 3),
            ('PFS', ctypes.c_uint32, 2),
            ('ETFS', ctypes.c_uint32, 1),
            ('L0SL', ctypes.c_uint32, 3),
            ('L1L', ctypes.c_uint32, 3),
            ('RSVD_0', ctypes.c_uint32, 3),
            ('RER', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 2),
            ('CSPLV', ctypes.c_uint32, 8),
            ('CSPLS', ctypes.c_uint32, 2),
            ('FLRC', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 3),
        ]

    class Pxdc(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('CERE', ctypes.c_uint16, 1),
            ('NFRE', ctypes.c_uint16, 1),
            ('FERE', ctypes.c_uint16, 1),
            ('URRE', ctypes.c_uint16, 1),
            ('ERO', ctypes.c_uint16, 1),
            ('MPS', ctypes.c_uint16, 3),
            ('ETE', ctypes.c_uint16, 1),
            ('PFE', ctypes.c_uint16, 1),
            ('APPME', ctypes.c_uint16, 1),
            ('ENS', ctypes.c_uint16, 1),
            ('MRRS', ctypes.c_uint16, 3),
            ('IFLR', ctypes.c_uint16, 1),
        ]

    class Pxds(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('CED', ctypes.c_uint16, 1),
            ('NFED', ctypes.c_uint16, 1),
            ('FED', ctypes.c_uint16, 1),
            ('URD', ctypes.c_uint16, 1),
            ('APD', ctypes.c_uint16, 1),
            ('TP', ctypes.c_uint16, 1),
            ('RSVD_0', ctypes.c_uint16, 10),
        ]

    class Pxlcap(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('SLS', ctypes.c_uint32, 4),
            ('MLW', ctypes.c_uint32, 6),
            ('ASPMS', ctypes.c_uint32, 2),
            ('L0SEL', ctypes.c_uint32, 3),
            ('L1EL', ctypes.c_uint32, 3),
            ('CPM', ctypes.c_uint32, 1),
            ('SDERC', ctypes.c_uint32, 1),
            ('DLLLA', ctypes.c_uint32, 1),
            ('LBNC', ctypes.c_uint32, 1),
            ('AOC', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 1),
            ('PN', ctypes.c_uint32, 8),
        ]

    class Pxlc(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('ASPMC', ctypes.c_uint16, 2),
            ('RSVD_0', ctypes.c_uint16, 1),
            ('RCB', ctypes.c_uint16, 1),
            ('RSVD_1', ctypes.c_uint16, 2),
            ('CCC', ctypes.c_uint16, 1),
            ('ES', ctypes.c_uint16, 1),
            ('ECPM', ctypes.c_uint16, 1),
            ('HAWD', ctypes.c_uint16, 1),
            ('RSVD_2', ctypes.c_uint16, 6),
        ]

    class Pxls(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('CLS', ctypes.c_uint16, 4),
            ('NLW', ctypes.c_uint16, 6),
            ('RSVD_0', ctypes.c_uint16, 2),
            ('SCC', ctypes.c_uint16, 1),
            ('RSVD_1', ctypes.c_uint16, 3),
        ]

    class Pxdcap2(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('CTRS', ctypes.c_uint32, 4),
            ('CTDS', ctypes.c_uint32, 1),
            ('ARIFS', ctypes.c_uint32, 1),
            ('AORS', ctypes.c_uint32, 1),
            ('32AOCS', ctypes.c_uint32, 1),
            ('64AOCS', ctypes.c_uint32, 1),
            ('128CCS', ctypes.c_uint32, 1),
            ('NPRPR', ctypes.c_uint32, 1),
            ('LTRS', ctypes.c_uint32, 1),
            ('TPHCS', ctypes.c_uint32, 2),
            ('RSVD_0', ctypes.c_uint32, 4),
            ('OBFFS', ctypes.c_uint32, 2),
            ('EFFS', ctypes.c_uint32, 1),
            ('EETPS', ctypes.c_uint32, 1),
            ('MEETP', ctypes.c_uint32, 2),
            ('RSVD_1', ctypes.c_uint32, 8),
        ]

    class Pxdc2(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('CTA', ctypes.c_uint32, 4),
            ('CTD', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 5),
            ('LTRME', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 2),
            ('OBFFE', ctypes.c_uint32, 2),
            ('RSVD_2', ctypes.c_uint32, 16),
        ]

    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint8),
        ('NEXT_PTR', ctypes.c_uint8),
        ('PXCAP', Pxcap),
        ('PXDCAP', Pxdcap),
        ('PXDC', Pxdc),
        ('PXDS', Pxds),
        ('PXLCAP', Pxlcap),
        ('PXLC', Pxlc),
        ('PXLS', Pxls),
        ('PXDCAP2', Pxdcap2),
        ('PXDC2', Pxdc2),
    ]


class PCICapabilityIdTable:
    ids = [PCICapabilityGen] * 0x15
    ids[0x01] = PCICapPowerManagementInterface
    ids[0x05] = PCICapMSI
    ids[0x10] = PCICapExpress
    ids[0x11] = PCICapMSIX


class PCICapabilityGenExtended(PCICapability):
    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint32, 16),
        ('CAP_VER', ctypes.c_uint32, 4),
        ('NEXT_PTR', ctypes.c_uint32, 12),
    ]


class PCICapExtendedAer(PCICapability):
    _cap_id_ = 0x1

    class Aeruces(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint32, 4),
            ('DLPES', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 7),
            ('PTS', ctypes.c_uint32, 1),
            ('FCPES', ctypes.c_uint32, 1),
            ('CTS', ctypes.c_uint32, 1),
            ('CAS', ctypes.c_uint32, 1),
            ('UCS', ctypes.c_uint32, 1),
            ('ROS', ctypes.c_uint32, 1),
            ('MTS', ctypes.c_uint32, 1),
            ('ECRCES', ctypes.c_uint32, 1),
            ('URES', ctypes.c_uint32, 1),
            ('ACSVS', ctypes.c_uint32, 1),
            ('UIES', ctypes.c_uint32, 1),
            ('MCBTS', ctypes.c_uint32, 1),
            ('AOEBS', ctypes.c_uint32, 1),
            ('TPBES', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 6),
        ]

    class Aerucem(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint32, 4),
            ('DLPEM', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 7),
            ('PTM', ctypes.c_uint32, 1),
            ('FCPEM', ctypes.c_uint32, 1),
            ('CTM', ctypes.c_uint32, 1),
            ('CAM', ctypes.c_uint32, 1),
            ('UCM', ctypes.c_uint32, 1),
            ('ROM', ctypes.c_uint32, 1),
            ('MTM', ctypes.c_uint32, 1),
            ('ECRCEM', ctypes.c_uint32, 1),
            ('UREM', ctypes.c_uint32, 1),
            ('ACSVM', ctypes.c_uint32, 1),
            ('UIEM', ctypes.c_uint32, 1),
            ('MCBTM', ctypes.c_uint32, 1),
            ('AOEBM', ctypes.c_uint32, 1),
            ('TPBEM', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 6),
        ]

    class Aerucesev(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint32, 4),
            ('DLPESEV', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 7),
            ('PTSEV', ctypes.c_uint32, 1),
            ('FCPESEV', ctypes.c_uint32, 1),
            ('CTSEV', ctypes.c_uint32, 1),
            ('CASEV', ctypes.c_uint32, 1),
            ('UCSEV', ctypes.c_uint32, 1),
            ('ROSEV', ctypes.c_uint32, 1),
            ('SEV', ctypes.c_uint32, 1),
            ('ECRCESEV', ctypes.c_uint32, 1),
            ('URESEV', ctypes.c_uint32, 1),
            ('ACSVSEV', ctypes.c_uint32, 1),
            ('UIESEV', ctypes.c_uint32, 1),
            ('SEV', ctypes.c_uint32, 1),
            ('AOEBSEV', ctypes.c_uint32, 1),
            ('TPBESEV', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 6),
        ]

    class Aerces(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('RES', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 5),
            ('BTS', ctypes.c_uint32, 1),
            ('BDS', ctypes.c_uint32, 1),
            ('RRS', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 3),
            ('RTS', ctypes.c_uint32, 1),
            ('ANFES', ctypes.c_uint32, 1),
            ('CIES', ctypes.c_uint32, 1),
            ('HLOS', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 16),
        ]

    class Aercem(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('REM', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 5),
            ('BTM', ctypes.c_uint32, 1),
            ('BDM', ctypes.c_uint32, 1),
            ('RRM', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 3),
            ('RTM', ctypes.c_uint32, 1),
            ('ANFEM', ctypes.c_uint32, 1),
            ('CIEM', ctypes.c_uint32, 1),
            ('HLOM', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 16),
        ]

    class Aercc(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('FEP', ctypes.c_uint32, 5),
            ('EGC', ctypes.c_uint32, 1),
            ('EGE', ctypes.c_uint32, 1),
            ('ECC', ctypes.c_uint32, 1),
            ('ECE', ctypes.c_uint32, 1),
            ('MHRC', ctypes.c_uint32, 1),
            ('MHRE', ctypes.c_uint32, 1),
            ('TPLP', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 20),
        ]

    class Aerhl(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('HB3', ctypes.c_uint8),
            ('HB2', ctypes.c_uint8),
            ('HB1', ctypes.c_uint8),
            ('HB0', ctypes.c_uint8),
            ('HB7', ctypes.c_uint8),
            ('HB6', ctypes.c_uint8),
            ('HB5', ctypes.c_uint8),
            ('HB4', ctypes.c_uint8),
            ('HB11', ctypes.c_uint8),
            ('HB10', ctypes.c_uint8),
            ('HB9', ctypes.c_uint8),
            ('HB8', ctypes.c_uint8),
            ('HB15', ctypes.c_uint8),
            ('HB14', ctypes.c_uint8),
            ('HB13', ctypes.c_uint8),
            ('HB12', ctypes.c_uint8),
        ]

    class Aertlp(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('TPL1B3', ctypes.c_uint8),
            ('TPL1B2', ctypes.c_uint8),
            ('TPL1B1', ctypes.c_uint8),
            ('TPL1B0', ctypes.c_uint8),
            ('TPL2B3', ctypes.c_uint8),
            ('TPL2B2', ctypes.c_uint8),
            ('TPL2B1', ctypes.c_uint8),
            ('TPL2B0', ctypes.c_uint8),
            ('TPL3B3', ctypes.c_uint8),
            ('TPL3B2', ctypes.c_uint8),
            ('TPL3B1', ctypes.c_uint8),
            ('TPL3B0', ctypes.c_uint8),
            ('TPL4B3', ctypes.c_uint8),
            ('TPL4B2', ctypes.c_uint8),
            ('TPL4B1', ctypes.c_uint8),
            ('TPL4B0', ctypes.c_uint8),
        ]

    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint32, 16),
        ('CAP_VER', ctypes.c_uint32, 4),
        ('NEXT_PTR', ctypes.c_uint32, 12),
        ('AERUCES', Aeruces),
        ('AERUCEM', Aerucem),
        ('AERUCESEV', Aerucesev),
        ('AERCES', Aerces),
        ('AERCEM', Aercem),
        ('AERCC', Aercc),
        ('AERHL', Aerhl),
        ('AERTLP', Aertlp),
    ]


class PCICapExtendeDeviceSerialNumber(PCICapability):
    _cap_id_ = 0x3

    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint32, 16),
        ('CAP_VER', ctypes.c_uint32, 4),
        ('NEXT_PTR', ctypes.c_uint32, 12),
        ('SN_LOW', ctypes.c_uint32),
        ('SN_HIGH', ctypes.c_uint32),
    ]


class PCICapabilityExtendedIdTable:
    ids = [PCICapabilityGenExtended] * 0x2C
    ids[0x01] = PCICapExtendedAer
    ids[0x03] = PCICapExtendeDeviceSerialNumber
