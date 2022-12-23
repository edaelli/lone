''' Models NVMe Specification registers
'''
import ctypes
import logging

from lone.util.struct_tools import ComparableStruct, StructFieldsIterator


class NVMeRegisters(ComparableStruct):
    ''' Controller registers from the NVMe specification
    '''

    class Cap(ComparableStruct):
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
            ('RSVD_1', ctypes.c_uint64, 2),
            ('MPSMIN', ctypes.c_uint64, 4),
            ('MPSMAX', ctypes.c_uint64, 4),
            ('PMRS', ctypes.c_uint64, 1),
            ('CMBS', ctypes.c_uint64, 1),
            ('RSVD_2', ctypes.c_uint64, 6),
        ]

    class Vs(ComparableStruct):
        _pack_ = 1
        _fields_ = [
            ('RSVD', ctypes.c_uint32, 8),
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

    class Pmrmsc(ComparableStruct):
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
        ('RSVD_1', ctypes.c_uint32 * 873),
        ('PMRCAP', Pmrcap),
        ('PMRCTL', Pmrctl),
        ('PMRSTS', Pmrsts),
        ('PMREBS', Pmrebs),
        ('PMRSWTP', Pmrswtp),
        ('PMRMSC', Pmrmsc),
        ('RSVD_2', ctypes.c_uint32 * 121),
        ('SQNDBS', Sqndbs * 1024),
    ]

    def log(self):
        log = logging.getLogger('nvme_regs')

        for field, value in StructFieldsIterator(self):
            if 'RSVD' not in field:
                log.debug('{:50} 0x{:x}'.format(field, value))
