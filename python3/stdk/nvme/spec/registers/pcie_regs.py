import os
import ctypes
import struct
import logging
from collections import namedtuple

from stdk.util.struct_tools import ComparableStruct, StructFieldsIterator


# namedtuple for storing information on how to access
#   pci registers in various implementations.
PCIeAccessData = namedtuple('PCIeAccessData', 'get_func set_func')


def pcie_reg_struct_factory(access_data):

    class PCIeRegsStruct(ComparableStruct):

        def __setattr__(self, name, value):

            if not self._access_.set_func:
                object.__setattr__(self, name, value)
            else:
                # Get pci registers offset and size for this structure
                size_bytes = ctypes.sizeof(self.__class__)
                offset = self._base_offset_

                # READ size_bytes from offset into a temporary buffer
                #   of the same type as ourselves
                read_data = self._access_.get_func(offset, size_bytes)
                read_obj = self.__class__.from_buffer(read_data)

                # MODIFY our read data with the new value at name
                super(PCIeRegsStruct, read_obj).__setattr__(name, value)

                # WRITE it back to the registers
                self._access_.set_func(offset, size_bytes, read_data)

        def __getattribute__(self, name):

            access = object.__getattribute__(self, '_access_')
            if not access.get_func:
                return object.__getattribute__(self, name)
            else:
                # If this is one of the fields in our structure, go read the latest
                #  value before returning
                fields = object.__getattribute__(self, '_fields_')
                if name in [f[0] for f in fields]:

                    # READ the latest value from registers
                    size_bytes = ctypes.sizeof(self.__class__)
                    offset = self._base_offset_
                    data_bytes = self._access_.get_func(offset, size_bytes)

                    # Create an object with the read value
                    data = self.__class__.from_buffer(data_bytes)
                    value = object.__getattribute__(data, name)

                    # Return it
                    return value

                else:
                    # Anything not in our fields, just call the base object
                    return object.__getattribute__(self, name)

    class NVMePCIeRegisters(PCIeRegsStruct):

        class Id(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('VID', ctypes.c_uint32, 16),
                ('DID', ctypes.c_uint32, 16),
            ]
            _access_ = access_data
            _base_offset_ = 0x00

        class Cmd(PCIeRegsStruct):
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

        class Sts(PCIeRegsStruct):
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

        class Cc(PCIeRegsStruct):
            _pack = 1
            _fields_ = [
                ('PI', ctypes.c_uint8),
                ('SCC', ctypes.c_uint8),
                ('BCC', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x09

        class Htype(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('HL', ctypes.c_uint8, 7),
                ('MFD', ctypes.c_uint8, 1),
            ]
            _access_ = access_data
            _base_offset_ = 0x0E

        class Bist(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('CC', ctypes.c_uint8, 4),
                ('RSVD_1', ctypes.c_uint8, 2),
                ('SB', ctypes.c_uint8, 1),
                ('BC', ctypes.c_uint8, 1),
            ]
            _access_ = access_data
            _base_offset_ = 0x0F

        class Bar0(PCIeRegsStruct):
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

        class Bar1(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('BA', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x14

        class Ss(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('SSVID', ctypes.c_uint16),
                ('SSID', ctypes.c_uint16),
            ]
            _access_ = access_data
            _base_offset_ = 0x2C

        class Erom(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('RBA', ctypes.c_uint32),
            ]
            _access_ = access_data
            _base_offset_ = 0x30

        class Cap(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('CP', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x34

        class Intr(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('ILINE', ctypes.c_uint8),
                ('IPIN', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x3C

        class Mgnt(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('GNT', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x3E

        class Mlat(PCIeRegsStruct):
            _pack_ = 1
            _fields_ = [
                ('LAT', ctypes.c_uint8),
            ]
            _access_ = access_data
            _base_offset_ = 0x3F

        ''' PCIe registers from the NVMe specification
        '''
        _pack_ = 1
        _fields_ = [
            ('ID', Id),
            ('CMD', Cmd),
            ('STS', Sts),
            ('RID', ctypes.c_uint8),
            ('CC', Cc),
            ('CLS', ctypes.c_uint8),
            ('MLT', ctypes.c_uint8),
            ('HTYPE', Htype),
            ('BIST', Bist),
            ('BAR0', Bar0),
            ('BAR1', Bar1),
            ('BAR2', ctypes.c_uint32),
            ('BAR3', ctypes.c_uint32),
            ('BAR4', ctypes.c_uint32),
            ('BAR5', ctypes.c_uint32),
            ('CCPTR', ctypes.c_uint32),
            ('SS', Ss),
            ('EROM', Erom),
            ('CAP', Cap),
            ('RSVD_0', ctypes.c_uint8 * 5),
            ('RSVD_1', ctypes.c_uint16),
            ('INTR', Intr),
            ('MGNT', Mgnt),
            ('MLAT', Mlat),

            # The rest of the space is for capabilities, and
            # extended capabilities
            ('RSVD_CAP', ctypes.c_uint8 * 4032),
        ]
        _access_ = access_data
        _base_offset_ = 0x00

    return NVMePCIeRegisters


class PCIeRegisters:

    def init_capabilities(self):
        self.capabilities = []

        # Make a copy of the capabilities data to loop through
        cap_data = bytearray([0] * ctypes.sizeof(self.registers))
        for i, r in enumerate(self.RSVD_CAP, start=type(self.registers).RSVD_CAP.offset):
            cap_data[i] = r

        # Walk regular and extended capabilities
        for next_cap_ptr in [self.CAP.CP, 0x100]:

            # Are we going over exteneded capabilities?
            if next_cap_ptr == 0x100:
                extended = True
            else:
                extended = False

            while next_cap_ptr:
                # For each capability create a cap object and add to our list
                b = cap_data[next_cap_ptr:next_cap_ptr + 4]

                cap = PCICapabilityGen.from_buffer_copy(b)

                # Figure out what capability this is
                if extended:
                    cap_obj = PCICapabilityExtendedIdTable.ids[cap.CAP_ID]
                else:
                    cap_obj = PCICapabilityIdTable.ids[cap.CAP_ID]

                # Now go read it and create the capabilities object
                size_bytes = ctypes.sizeof(cap_obj)
                data = bytearray()
                for i in range(size_bytes):
                    data += cap_data[next_cap_ptr + i].to_bytes(1, 'big')

                cap = cap_obj.from_buffer_copy(data)

                # Add it to our list and log it
                self.capabilities.append(cap)
                # cap.log()

                # Advance to the next one
                next_cap_ptr = cap.NEXT_PTR

    def log(self):
        log = logging.getLogger('pcie_regs')
        for field, value in StructFieldsIterator(self.registers):
            if 'RSVD' not in field:
                log.debug('{:50} 0x{:x}'.format(field, value))


class PCIeRegistersDirect(pcie_reg_struct_factory(PCIeAccessData(None, None)), PCIeRegisters):

    def __getattr__(self, name):

        # We dont need/use a registers attribute, but if code wants it
        #  self is the equivalent
        if name == 'registers':
            return self

        # Anything else is an AttributeError
        raise AttributeError('{} object has no attribute attribute "{}"'.format(
                             self.__class__.__name__, name))


class PCIeRegistersIndirect(PCIeRegisters):

    def __init__(self, fd, base_offset, size):
        # Create our access data
        self.registers = pcie_reg_struct_factory(PCIeAccessData(self.pcie_get, self.pcie_set))()
        self.fd = fd
        self.base_offset = base_offset
        self.size = size

    def pcie_get(self, offset, size_bytes):
        data = os.pread(self.fd, size_bytes, self.base_offset + offset)
        return bytearray(data)

    def pcie_set(self, offset, size_bytes, values):
        assert size_bytes == os.pwrite(self.fd, bytes(values), self.base_offset + offset)

    def __getattr__(self, name):

        # Is this a field we can indirectly read?
        if name != 'registers' and name in dir(self.registers):
            field = [f for f in self.registers._fields_ if f[0] == name][0]
            field_class = field[1]
            offset = getattr(type(self.registers), name).offset
            size_bytes = getattr(type(self.registers), name).size

            # Read current PCI config register(s)
            data = self.pcie_get(offset, size_bytes)

            # Create an object of the correct type and return it
            if issubclass(field_class, ctypes.Structure):
                # If this is a structure, just create one from the
                #  bytes we just read and return it
                return field_class.from_buffer(data)

            elif issubclass(field_class, ctypes.Array):
                # If this is a ctypes array, just return the array
                return data

            else:
                # convert to integer, the PCIe registers structure only
                #  has 8 and 32 sized attributes for now.
                if size_bytes == 1:
                    v = struct.unpack('B', data)[0]
                elif size_bytes == 4:
                    v = struct.unpack('I', data)[0]
                else:
                    # There is really no way to get here as the PCIe structure
                    #  does not have anything other than 1 and 4 byte values except
                    #  for testing (RSVD_1)
                    raise AttributeError('Do not understand type: {}'.format(type(field_class)))
                return v

        # Invalid attribute
        raise AttributeError('{} object has no attribute attribute "{}"'.format(
                             self.__class__.__name__, name))

    def __setattr__(self, name, value):

        if name != 'registers' and name in dir(self.registers):
            field = [f for f in self.registers._fields_ if f[0] == name][0]
            field_class = field[1]
            offset = getattr(type(self.registers), name).offset
            size_bytes = getattr(type(self.registers), name).size

            if issubclass(field_class, ctypes.Structure):
                # TODO: is this accurate??
                values = bytearray(getattr(self, name))

            elif issubclass(field_class, ctypes.Array):
                # TODO Check if value is an array type
                values = value[:size_bytes]
            else:
                # TODO Check if big is the right endian here
                values = value.to_bytes(size_bytes, 'big')
            self.pcie_set(offset, size_bytes, values)
        else:
            object.__setattr__(self, name, value)


class PCICapability(ctypes.Structure):

    def log(self):
        log = logging.getLogger('capability')

        log.debug('\n')
        log.debug('{}: next 0x{:x}'.format(
                  self.__class__.__name__, self.NEXT_PTR))

        for field, value in StructFieldsIterator(self):
            if 'RSVD' not in field:
                log.debug('{:50} 0x{:x}'.format(field, value))


class PCICapabilityGen(PCICapability):
    _pack_ = 1
    _fields_ = [
        ('CAP_ID', ctypes.c_uint8),
        ('NEXT_PTR', ctypes.c_uint8),
        ('CAP_REG', ctypes.c_uint16),
    ]


class PCICapPowerManagementInterface(PCICapability):
    cap_id = 0x1

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
    cap_id = 0x05

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
    cap_id = 0x11

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
    cap_id = 0x10

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
    cap_id = 0x1

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
    cap_id = 0x3

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
