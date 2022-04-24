import ctypes
from collections import namedtuple


class DptrPrp(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('PRP1', ctypes.c_uint64),
        ('PRP2', ctypes.c_uint64),
    ]


class DptrSgl(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('SGL1', ctypes.c_uint64 * 2),
    ]


class Dptr(ctypes.Union):
    _fields_ = [
        ('PRP', DptrPrp),
        ('SGL', DptrSgl),
    ]


class SQECommon(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('OPC', ctypes.c_uint32, 8),
        ('FUSE', ctypes.c_uint32, 2),
        ('RSVD_0', ctypes.c_uint32, 4),
        ('PSDT', ctypes.c_uint32, 2),
        ('CID', ctypes.c_uint32, 16),

        ('NSID', ctypes.c_uint32),

        ('DW2', ctypes.c_uint32),
        ('DW3', ctypes.c_uint32),

        ('MPTR', ctypes.c_uint64),

        ('DPTR', Dptr),
    ]
    data_in = None
    data_out = None

    db_ring_ns = None
    completion_found_ns = None

    def __init__(self, **kwargs):

        # Initialize defaults
        if hasattr(type(self), '_defaults_'):
            values = type(self)._defaults_.copy()
            for k, v in values.items():
                values[k] = v
            super().__init__(**values)
        super().__init__(**kwargs)

    def __len__(self):
        return ctypes.sizeof(self)

    def __setattr__(self, name, value):

        # Only allowed to set existing values
        if name not in dir(self):
            raise AttributeError('{} is not an attribute in {}'.format(name,
                                 self.__class__.__name__))
        else:
            object.__setattr__(self, name, value)


class DataOutCommon(ctypes.Structure):
    _pack_ = 1

    def __len__(self):
        return ctypes.sizeof(self)


class DataInCommon(ctypes.Structure):
    _pack_ = 1

    def __len__(self):
        return ctypes.sizeof(self)


class Generic(SQECommon):
    _fields_ = [
        ('DW10', ctypes.c_uint32),
        ('DW11', ctypes.c_uint32),
        ('DW12', ctypes.c_uint32),
        ('DW13', ctypes.c_uint32),
        ('DW14', ctypes.c_uint32),
        ('DW15', ctypes.c_uint32),
    ]


class ADMINCommand(SQECommon):
    cmdset_admin = True
    cmdset_nvm = False


class NVMCommand(SQECommon):
    cmdset_admin = False
    cmdset_nvm = True


class CQE(ctypes.Structure):

    class Sf(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('P', ctypes.c_uint16, 1),
            ('SC', ctypes.c_uint16, 8),
            ('SCT', ctypes.c_uint16, 3),
            ('CRD', ctypes.c_uint16, 2),
            ('M', ctypes.c_uint16, 1),
            ('DNR', ctypes.c_uint16, 1),
        ]

    _pack_ = 1
    _fields_ = [
        ('CMD_SPEC', ctypes.c_uint32),
        ('RSVD_0', ctypes.c_uint32),
        ('SQHD', ctypes.c_uint32, 16),
        ('SQID', ctypes.c_uint32, 16),
        ('CID', ctypes.c_uint16),
        ('SF', Sf),
    ]

    # It is kinda weird how the spec defines
    #   the P bit. It is not part of the SF structure
    #   but it is a 1 bit in the middle of a 32 bit field.
    #   Rather than trying to make a structure that fits that,
    #   just "cheat" here and use __getattr__/__setattr__ when
    #   a caller accesses it.
    def __getattr__(self, name):
        if name == 'P':
            return self.SF.P
        raise AttributeError('{} not in {}'.format(name, self.__class__.__name__))

    def __setattr__(self, name, value):
        if name == 'P':
            self.SF.P = value
        else:
            object.__setattr__(self, name, value)

    def __len__(self):
        return ctypes.sizeof(self)


ADMINStatusValue = namedtuple('ADMINStatusValue', 'status value')
NVMStatusValue = namedtuple('NVMStatusValue', 'status value')
