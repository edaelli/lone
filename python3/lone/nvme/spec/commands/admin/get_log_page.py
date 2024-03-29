import ctypes
from lone.nvme.spec.structures import ADMINCommand, DataInCommon
from lone.nvme.spec.commands.status_codes import NVMeStatusCode, status_codes


class GetLogPage(ADMINCommand):
    _pack_ = 1
    _fields_ = [
        ('LID', ctypes.c_uint32, 8),
        ('LSP', ctypes.c_uint32, 7),
        ('RAE', ctypes.c_uint32, 1),
        ('NUMDL', ctypes.c_uint32, 16),

        ('NUMDU', ctypes.c_uint32, 16),
        ('LID_SPEC', ctypes.c_uint32, 16),

        ('LPOL', ctypes.c_uint32),

        ('LPOU', ctypes.c_uint32),

        ('UUID_IDX', ctypes.c_uint32, 7),
        ('RSVD_0', ctypes.c_uint32, 16),
        ('OT', ctypes.c_uint32, 1),
        ('CSI', ctypes.c_uint32, 8),

        ('DW15', ctypes.c_uint32),
    ]

    _defaults_ = {
        'OPC': 0x02
    }


status_codes.add([
    NVMeStatusCode(0x09, 'Invalid Log Page', GetLogPage),
    NVMeStatusCode(0x29, 'I/O Command Set Not Supported', GetLogPage),
])


def GetLogPageFactory(name, lid, data_in_type):
    cls = type(name, (GetLogPage,), {"__init__": GetLogPage.__init__})
    cls.LID = lid
    cls.data_in_type = data_in_type
    cls.data_in_type.size = ctypes.sizeof(data_in_type)

    # Fill in number of DWORDS U/L for this command
    num_dw = int(ctypes.sizeof(data_in_type) / 4) - 1
    cls.NUMDL = num_dw & 0xFFFF
    cls.NUMDH = num_dw >> 16
    return cls


class GetLogPageSupportedLogPagesData(DataInCommon):

    class LIDSupportedAndEffectsData(ctypes.Structure):
        _pack_ = 1

        class LIDSupportedAndEffectsDataLIDSPECD(ctypes.Structure):
            _pack_ = 1
            _fields_ = [
                ('ESTCTXRD512HDSUP', ctypes.c_uint16, 1),
                ('RSVD_0', ctypes.c_uint16, 15),
            ]

        _fields_ = [
            ('LSUPP', ctypes.c_uint32, 1),
            ('IOS', ctypes.c_uint32, 1),
            ('RSVD_0', ctypes.c_uint32, 14),  # IS THIS A BUG IN THE SPEC???
            ('LIDSPEC', ctypes.c_uint32, 16)
        ]

    _fields_ = [
        # Note: When using LID 0x0D, the caller can do a
        # GetLogPageSupportedLogPagesData.LIDSupportedAndEffectsDataLIDSPECD.from_buffer
        #   to get the right type on the LIDS data.
        ('LIDS', LIDSupportedAndEffectsData * 256),
    ]


GetLogPageSupportedLogPages = GetLogPageFactory('GetLogPageSupportedLogPages',
                                                0x00,
                                                GetLogPageSupportedLogPagesData)

assert ctypes.sizeof(GetLogPageSupportedLogPagesData) == 1024


class GetLogPageErrorInformationData(DataInCommon):

    class ErrorInformationEntry(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('ErrorCount', ctypes.c_uint64),
            ('SQID', ctypes.c_uint16),
            ('CID', ctypes.c_uint16),

            ('P', ctypes.c_uint16, 1),
            ('SF', ctypes.c_uint16, 15),

            ('ParameterErrLocByte', ctypes.c_uint16, 8),
            ('ParameterErrLocBit', ctypes.c_uint16, 3),
            ('RSVD_0', ctypes.c_uint16, 5),

            ('LBA', ctypes.c_uint64),
            ('NS', ctypes.c_uint32),
            ('VSINFO', ctypes.c_uint8),
            ('TRTYPE', ctypes.c_uint8),
            ('RSVD_1', ctypes.c_uint16),
            ('CMDSPECINFO', ctypes.c_uint64),
            ('TRTYPESPECINFO', ctypes.c_uint16),
            ('RSVD_2', ctypes.c_uint8 * 22),
        ]

    _pack_ = 1
    _fields_ = [
        ('ERRORS', ErrorInformationEntry * 256),
    ]


GetLogPageErrorInformation = GetLogPageFactory('GetLogPageErrorInformation',
                                               0x01,
                                               GetLogPageErrorInformationData)

assert ctypes.sizeof(GetLogPageErrorInformationData) == 16384


class GetLogPageSMARTData(DataInCommon):

    class CriticalWarning(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('AvailableSpareBelowThreshold', ctypes.c_uint8, 1),
            ('TemperatureThreshold', ctypes.c_uint8, 1),
            ('NVMeSubsystemReliabilityDegraded', ctypes.c_uint8, 1),
            ('ReadOnlyMode', ctypes.c_uint8, 1),
            ('VolatileMemBackupFailed', ctypes.c_uint8, 1),
            ('PersistentMemRegionReadOnly', ctypes.c_uint8, 1),
            ('RSVD_0', ctypes.c_uint8, 2),
        ]

    class EnduranceGroupCriticalWarning(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('AvailableSpareBelowThreshold', ctypes.c_uint8, 1),
            ('RSVD_0', ctypes.c_uint8, 1),
            ('ReliabilityDegraded', ctypes.c_uint8, 1),
            ('NamespaceInReadOnlyMode', ctypes.c_uint8, 1),
            ('RSVD_1', ctypes.c_uint8, 4),
        ]

    class TemperatureSensorData(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ('TST', ctypes.c_uint16),
        ]

    _pack_ = 1
    _fields_ = [
        ('CriticalWarning', CriticalWarning),
        ('CompositeTemperature', ctypes.c_uint16),
        ('AvailableSpare', ctypes.c_uint8),
        ('AvailableSpareThreshold', ctypes.c_uint8),
        ('PercentageUsed', ctypes.c_uint8),
        ('EnduranceGrpCriticalWarnSummary', EnduranceGroupCriticalWarning),
        ('RSVD_0', ctypes.c_uint8 * 25),
        ('DataUnitsReadLo', ctypes.c_uint64),
        ('DataUnitsReadHi', ctypes.c_uint64),
        ('DataUnitsWrittenLo', ctypes.c_uint64),
        ('DataUnitsWrittenHi', ctypes.c_uint64),
        ('HostReadCommandsLo', ctypes.c_uint64),
        ('HostReadCommandsHi', ctypes.c_uint64),
        ('HostWriteCommandsLo', ctypes.c_uint64),
        ('HostWriteCommandsHi', ctypes.c_uint64),
        ('ControllerBusyTimeLo', ctypes.c_uint64),
        ('ControllerBusyTimeHi', ctypes.c_uint64),
        ('PowerCyclesLo', ctypes.c_uint64),
        ('PowerCyclesHi', ctypes.c_uint64),
        ('PowerOnHoursLo', ctypes.c_uint64),
        ('PowerOnHoursHi', ctypes.c_uint64),
        ('UnsafeShutdownsLo', ctypes.c_uint64),
        ('UnsafeShutdownsHi', ctypes.c_uint64),
        ('MediaAndDataIntegrityErrorsLo', ctypes.c_uint64),
        ('MediaAndDataIntegrityErrorsHi', ctypes.c_uint64),
        ('NumberofErrorInformationLogEntriesLo', ctypes.c_uint64),
        ('NumberofErrorInformationLogEntriesHi', ctypes.c_uint64),
        ('WarningCompTempTime', ctypes.c_uint32),
        ('CriticalCompTempTime', ctypes.c_uint32),
        ('TempSensors', TemperatureSensorData * 8),
        ('ThermalMgmtTemp1TransitionCount', ctypes.c_uint32),
        ('ThermalMgmtTemp2TransitionCount', ctypes.c_uint32),
        ('TotalTimeThermalMgmtTemp1', ctypes.c_uint32),
        ('TotalTimeThermalMgmtTemp2', ctypes.c_uint32),
        ('RSVD_1', ctypes.c_uint8 * 280),
    ]


GetLogPageSMART = GetLogPageFactory('GetLogPageSMART',
                                    0x02,
                                    GetLogPageSMARTData)

# Perform some checks to make sure it matches the spec
assert ctypes.sizeof(GetLogPageSMARTData) == 512
assert GetLogPageSMARTData.ThermalMgmtTemp2TransitionCount.offset == 220
assert GetLogPageSMARTData.ControllerBusyTimeLo.offset == 96


class GetLogPageFirmwareSlotInfoData(DataInCommon):
    _pack_ = 1
    _fields_ = [
        ('AFI', ctypes.c_uint8),
        ('RSVD_0', ctypes.c_uint8 * 7),
        ('FRS1', ctypes.c_char * 8),
        ('FRS2', ctypes.c_char * 8),
        ('FRS3', ctypes.c_char * 8),
        ('FRS4', ctypes.c_char * 8),
        ('FRS5', ctypes.c_char * 8),
        ('FRS6', ctypes.c_char * 8),
        ('FRS7', ctypes.c_char * 8),
        ('RSVD_0', ctypes.c_uint8 * 448),
    ]


GetLogPageFirmwareSlotInfo = GetLogPageFactory('GetLogPageFirmwareSlotInfo',
                                               0x03,
                                               GetLogPageFirmwareSlotInfoData)

# Perform some checks to make sure it matches the spec
assert ctypes.sizeof(GetLogPageFirmwareSlotInfoData) == 512
assert GetLogPageFirmwareSlotInfoData.FRS3.offset == 24
