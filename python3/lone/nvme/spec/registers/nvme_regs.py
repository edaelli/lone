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
            ('IVMS', ctypes.c_uint32),
        ]

    class Intmc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('IVMC', ctypes.c_uint32),
        ]

    class Cc(ComparableStruct):

        class Css(enum.Enum):
            NVM_COMMAND_SET = 0x00
            ALL_SUPPORTED_COMMAND_SETS = 0x06
            ADMIN_COMMAND_SET_ONLY = 0x07

        class Ams(enum.Enum):
            ROUND_ROBIN = 0x0
            WEIGHTED_ROUND_ROBIN_W_URG_PRIO_CLASS = 0x1
            VENDOR_SPECIFIC = 0x7

        class Shn(enum.Enum):
            NO_NOTIFICATION = 0
            NORMAL_SHUTDOWN = 1
            ABRUPT_SHUTDOWN = 2

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
            ('CRIME', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 7),
        ]

    class Csts(ComparableStruct):

        class Shst(enum.Enum):
            NORMAL_OPERATION = 0x0
            SHUTDOWN_PROCESSING_OCCURRING = 0x01
            SHUTDOWN_PROCESSING_COMPLETE = 0x02

        _pack_ = 1
        _fields_ = [
            ('RDY', ctypes.c_uint32, 1),
            ('CFS', ctypes.c_uint32, 1),
            ('SHST', ctypes.c_uint32, 2),
            ('NSSRO', ctypes.c_uint32, 1),
            ('PP', ctypes.c_uint32, 1),
            ('ST', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 25),
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
            ('ASQB', ctypes.c_uint64, 52),
            ('RSVD_0', ctypes.c_uint64, 12),
        ]

    class Acq(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('ACQB', ctypes.c_uint64, 52),
            ('RSVD_0', ctypes.c_uint64, 12),
        ]

    class Cmbloc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('BIR', ctypes.c_uint32, 3),
            ('CQMMS', ctypes.c_uint32, 1),
            ('CQPDS', ctypes.c_uint32, 1),
            ('CQPMLS', ctypes.c_uint32, 1),
            ('CDPCILS', ctypes.c_uint32, 1),
            ('CDMMMS', ctypes.c_uint32, 1),
            ('CQDA', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 3),
            ('OFST', ctypes.c_uint32, 20),
        ]

    class Cmbsz(ComparableStruct):

        class Szu(enum.Enum):
            SZU_4KiB = 0x0
            SZU_64KiB = 0x1
            SZU_1MiB = 0x2
            SZU_16MiB = 0x3
            SZU_256MiB = 0x4
            SZU_4GiB = 0x5
            SZU_64GiB = 0x6

        _pack_ = 1
        _fields_ = [
            ('SQS', ctypes.c_uint32, 1),
            ('CQS', ctypes.c_uint32, 1),
            ('LISTS', ctypes.c_uint32, 1),
            ('RDS', ctypes.c_uint32, 1),
            ('WDS', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 3),
            ('SZU', ctypes.c_uint32, 4),
            ('SZ', ctypes.c_uint32, 20),
        ]

    class Bpinfo(ComparableStruct):

        class Brs(enum.Enum):
            NO_BOOT_PARTITION_RD_OP_REQ = 0x0
            BOOT_PARTITION_RD_IN_PROGRESS = 0x1
            BOOT_PARTITION_RD_COMPLETE_SUCCESSFULLY = 0x2
            BOOT_ERROR_COMPLETING_BOOT_PARTITION_READ = 0x3

        _pack_ = 1
        _fields_ = [
            ('BPSZ', ctypes.c_uint32, 15),
            ('RSVD_0', ctypes.c_uint32, 9),
            ('BRS', ctypes.c_uint32, 2),
            ('RSVD_1', ctypes.c_uint32, 5),
            ('ABPID', ctypes.c_uint32, 1),
        ]

    class Bprsel(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('BPRSZ', ctypes.c_uint32, 10),
            ('BPROF', ctypes.c_uint32, 20),
            ('RSVD_0', ctypes.c_uint32, 1),
            ('BPID', ctypes.c_uint32, 1),
        ]

    class Bpmbl(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint64, 12),
            ('BMBBA', ctypes.c_uint64, 52),
        ]

    class Cmbmsc(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('CRE', ctypes.c_uint64, 1),
            ('CMSE', ctypes.c_uint64, 1),
            ('RSVD_0', ctypes.c_uint64, 10),
            ('CBA', ctypes.c_uint64, 52),
        ]

    class Cmbsts(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('CBAI', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 31),
        ]

    class Cmbebs(ComparableStruct):

        class Cmbszu(enum.Enum):
            SZU_BYTES = 0x0
            SZU_1KiB = 0x1
            SZU_1MiB = 0x2
            SZU_1GiB = 0x3

        _pack_ = 1
        _fields_ = [
            ('CMBSZU', ctypes.c_uint32, 4),
            ('RBB', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 3),
            ('CMBWBZ', ctypes.c_uint32, 24),
        ]

    class Cmbswtp(ComparableStruct):

        class Cmbswtu(enum.Enum):
            TU_BYTES_PER_SECOND = 0x0
            TU_KiB_PER_SECOND = 0x1
            TU_MiB_PER_SECOND = 0x2
            TU_GiB_PER_SECOND = 0x3

        _pack_ = 1
        _fields_ = [
            ('CMBSWTU', ctypes.c_uint32, 4),
            ('RSVD_0', ctypes.c_uint32, 4),
            ('CMBSWTV', ctypes.c_uint32, 24),
        ]

    class Nssd(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('NSSC', ctypes.c_uint32),
        ]

    class Crto(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('CRWMT', ctypes.c_uint32, 16),
            ('CRIMT', ctypes.c_uint32, 16),
        ]

    class Pmrcap(ComparableStruct):

        class Pmrtu(enum.Enum):
            TU_500_MS = 0x0
            TU_MINUTES = 0x1

        class Pmrwbm(enum.Enum):
            READS_ENSURED = 0
            WRITES_ENSURED = 1

        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint32, 3),
            ('RDS', ctypes.c_uint32, 1),
            ('WDS', ctypes.c_uint32, 1),
            ('BIR', ctypes.c_uint32, 3),
            ('PMRTU', ctypes.c_uint32, 2),
            ('PMRWBM', ctypes.c_uint32, 4),
            ('RSVD_1', ctypes.c_uint32, 2),
            ('PMRTO', ctypes.c_uint32, 8),
            ('CMSS', ctypes.c_uint32, 1),
            ('RSVD_2', ctypes.c_uint32, 7),
        ]

    class Pmrctl(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('EN', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 31),
        ]

    class Pmrsts(ComparableStruct):

        class Hsts(enum.Enum):
            NORMAL_OPERATION = 0x00
            RESTORE_ERROR = 0x01
            READ_ONLY = 0x02
            UNRELIABLE = 0x03

        _pack_ = 1
        _fields_ = [
            ('ERR', ctypes.c_uint32, 8),
            ('NRDY', ctypes.c_uint32, 1),
            ('HSTS', ctypes.c_uint32, 3),
            ('CBAI', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 19),
        ]

    class Pmrebs(ComparableStruct):

        class Pmrszu(enum.Enum):
            SZU_BYTES = 0x0
            SZU_1KiB = 0x1
            SZU_1MiB = 0x2
            SZU_1GiB = 0x3

        _pack_ = 1
        _fields_ = [
            ('PMRSZU', ctypes.c_uint32, 4),
            ('RBB', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 3),
            ('PMRWBZ', ctypes.c_uint32, 24),
        ]

    class Pmrswtp(ComparableStruct):

        class Pmrswtu(enum.Enum):
            TU_BYTES_PER_SECOND = 0x0
            TU_KiB_PER_SECOND = 0x1
            TU_MiB_PER_SECOND = 0x2
            TU_GiB_PER_SECOND = 0x3

        _pack_ = 1
        _fields_ = [
            ('PMRSWTU', ctypes.c_uint32, 4),
            ('RSVD_0', ctypes.c_uint32, 4),
            ('PMRSWTV', ctypes.c_uint32, 24),
        ]

    class Pmrmscl(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('RSVD_0', ctypes.c_uint32, 1),
            ('CMSE', ctypes.c_uint32, 1),
            ('RSVD_1', ctypes.c_uint32, 10),
            ('CBA', ctypes.c_uint32, 20),
        ]

    class Pmrmscu(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('CBA', ctypes.c_uint32),
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
