''' Models NVMe Specification registers
'''
import ctypes
import enum
import logging

from lone.util.struct_tools import ComparableStruct, StructFieldsIterator


class NVMeRegisters(ComparableStruct):
    ''' Controller registers from the NVMe specification
    '''

    class Cap(ComparableStruct):

        class AMS(enum.Enum):
            # Arbitration Mechanism Supported
            WEIGHTED_ROUND_ROBIN_WITH_URGENT_PRIORITY_CLASS = 0
            VENDOR_SPECIFIC = 1

        class CSS(enum.Enum):
            # Command Sets Supported
            NVM_COMMAND_SET = 0x01
            ONE_OR_MORE_IO_CMD_SETS = 0x40
            NO_IO_CMD_SETS = 0x80

        class CPS(enum.Enum):
            # Controller Power Scope
            NOT_REPORTED = 0
            CONTROLLER_SCOPE = 1
            DOMAIN_SCOPE = 2
            NVM_SUBSYSTEM_SCOPE = 3

        class CRMS(enum.Enum):
            # Controller Ready Modes Supported
            CONTROLLER_READY_WITH_MEDIA_SUPPORT = 0
            CONTROLLER_READY_INDEPENDENT_OF_MEDIA_SUPPORT = 1

        _pack_ = 1
        _fields_ = [
            ('MQES', ctypes.c_uint64, 16),
            ('CQR', ctypes.c_uint64, 1),
            ('AMS', ctypes.c_uint64, 2),
            ('RSVD_0', ctypes.c_uint64, 5),
            ('TO', ctypes.c_uint64, 8),
            ('DSTRD', ctypes.c_uint64, 4),
            ('NSSRS', ctypes.c_uint64, 1),
            ('CSS', ctypes.c_uint64, 8),
            ('BPS', ctypes.c_uint64, 1),
            ('CPS', ctypes.c_uint64, 2),
            ('MPSMIN', ctypes.c_uint64, 4),
            ('MPSMAX', ctypes.c_uint64, 4),
            ('PMRS', ctypes.c_uint64, 1),
            ('CMBS', ctypes.c_uint64, 1),
            ('NSSS', ctypes.c_uint64, 1),
            ('CRMS', ctypes.c_uint64, 2),
            ('RSVD_2', ctypes.c_uint64, 3),
        ]

    class Vs(ComparableStruct):
        @property
        def __str__(self):
            return '{}.{}.{}'.format(self.MJR, self.MNR, self.TER)

        _pack_ = 1
        _fields_ = [
            ('TER', ctypes.c_uint32, 8),
            ('MNR', ctypes.c_uint32, 8),
            ('MJR', ctypes.c_uint32, 16),
        ]

    class Intms(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Intmc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Cc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('EN', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 3),
            ('CSS', ctypes.c_uint32, 3),
            ('MPS', ctypes.c_uint32, 4),
            ('AMS', ctypes.c_uint32, 3),
            ('SHN', ctypes.c_uint32, 2),
            ('IOSQES', ctypes.c_uint32, 4),
            ('IOCQES', ctypes.c_uint32, 4),
            ('RSVD_2', ctypes.c_uint32, 8),
        ]

    class Csts(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('RDY', ctypes.c_uint32, 1),
            ('CFS', ctypes.c_uint32, 1),
            ('SHST', ctypes.c_uint32, 2),
            ('NSSRO', ctypes.c_uint32, 1),
            ('PP', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 26),
        ]

    class Nssr(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('NSSRC', ctypes.c_uint32),
        ]

    class Aqa(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('ASQS', ctypes.c_uint32, 12),
            ('RSVD_0', ctypes.c_uint32, 4),
            ('ACQS', ctypes.c_uint32, 12),
            ('RSVD_1', ctypes.c_uint32, 4),
        ]

    class Asq(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('ASQB', ctypes.c_uint64),
        ]

    class Acq(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('ACQB', ctypes.c_uint64),
        ]

    class Cmbloc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Cmbsz(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Bpinfo(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Bprsel(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Bpmbl(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint64),
        ]

    class Cmbmsc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint64),
        ]

    class Cmbsts(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Cmbebs(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Cmbswtp(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Nssd(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Crto(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Pmrcap(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Pmrctl(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Pmrsts(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Pmrebs(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Pmrswtp(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint32),
        ]

    class Pmrmscl(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint64),
        ]

    class Pmrmscu(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('TBD', ctypes.c_uint64),
        ]

    class Sqndbs(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('SQTAIL', ctypes.c_uint32),
            ('CQHEAD', ctypes.c_uint32),
            # TODO: ADD EXTRA STRIDE HERE?
        ]

    _pack_ = 1
    _fields_ = [
        ('CAP', Cap),
        ('VS', Vs),
        ('INTMS', Intms),
        ('INTMC', Intmc),
        ('CC', Cc),
        ('RSVD_0', ctypes.c_uint32),
        ('CSTS', Csts),
        ('NSSR', Nssr),
        ('AQA', Aqa),
        ('ASQ', Asq),
        ('ACQ', Acq),
        ('CMBLOC', Cmbloc),
        ('CMBSZ', Cmbsz),
        ('BPINFO', Bpinfo),
        ('BPRSEL', Bprsel),
        ('BPMBL', Bpmbl),
        ('CMBMSC', Cmbmsc),
        ('CMBSTS', Cmbsts),
        ('CMBEBS', Cmbebs),
        ('CMBSWTP', Cmbswtp),
        ('NSSD', Nssd),
        ('CRTO', Crto),
        ('RSVD_1', ctypes.c_uint32 * 868),
        ('PMRCAP', Pmrcap),
        ('PMRCTL', Pmrctl),
        ('PMRSTS', Pmrsts),
        ('PMREBS', Pmrebs),
        ('PMRSWTP', Pmrswtp),
        ('PMRMSCL', Pmrmscl),
        ('PMRMSCU', Pmrmscu),
        ('RSVD_2', ctypes.c_uint32 * 120),
        ('SQNDBS', Sqndbs * 1024),
    ]

    def log(self):
        log = logging.getLogger('nvme_regs')

        for field, value in StructFieldsIterator(self):
            if 'RSVD' not in field:
                log.debug('{:50} 0x{:x}'.format(field, value))
