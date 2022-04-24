import os
import ctypes
import pytest


@pytest.fixture(scope='function')
def mocked_pci_regs():
    from stdk.nvme.spec.registers.pcie_regs import PCIeRegistersDirect
    return PCIeRegistersDirect()


@pytest.fixture(scope='function')
def mocked_nvme_regs():
    from stdk.nvme.spec.registers.nvme_regs import NVMeRegisters
    return NVMeRegisters()


@pytest.fixture(scope='function')
def mocked_nvme_device(mocked_pci_regs, mocked_nvme_regs):

    from stdk.nvme.device import NVMeDevice

    class NVMeDeviceTest(NVMeDevice):
        def __init__(self, pci_slot):
            self.pcie_regs = mocked_pci_regs
            self.nvme_regs = mocked_nvme_regs
            self.namespaces = []

        def map_dma_region_read(self, vaddr, iova, size):
            pass

        def map_dma_region_write(self, vaddr, iova, size):
            pass

        def map_dma_region_rw(self, vaddr, iova, size):
            pass

        def unmap_dma_region(self, iova, size):
            pass

    return NVMeDeviceTest


@pytest.fixture(scope='function')
def mocked_nvme_command():

    from stdk.nvme.spec.structures import SQECommon, DataInCommon, DataOutCommon

    class DataInTest(DataInCommon):
        size = 4096
        _fields_ = [
            ('FIELD_0', ctypes.c_uint8)
        ]

    class DataOutTest(DataOutCommon):
        size = 4096
        _fields_ = [
            ('FIELD_0', ctypes.c_uint8)
        ]

    class CommandTest(SQECommon):
        _fields_ = [
            ('DWORD10', ctypes.c_uint32),
            ('DWORD11', ctypes.c_uint32),
            ('DWORD12', ctypes.c_uint32),
            ('DWORD13', ctypes.c_uint32),
            ('DWORD14', ctypes.c_uint32),
            ('DWORD15', ctypes.c_uint32),
        ]
        data_out = DataOutTest()
        data_in = DataInTest()
        cmdset_admin = False
        cmdset_nvm = False

    return CommandTest


@pytest.fixture(scope='function') # noqa: C901
def mocked_system(mocker, mocked_pci_regs, mocked_nvme_regs): # noqa: C901

    from stdk.system import SysRequirements

    class TestSysRequirements(SysRequirements):
        def check_requirements(self):
            pass

    from stdk.system import SysPci
    from stdk.system import SysPciDevice

    class TestSysPci(SysPci):
        def rescan(self):
            pass

    class TestSysPciDevice(SysPciDevice):

        def exists(self):
            return True

        def remove(self):
            pass

        def expose(self, user):
            self.exposed_device_path = ''
            return

        def reclaim(self, driver):
            pass

    from stdk.system import SysPciUserspace
    from stdk.system import SysPciUserspaceDevice

    class TestSysPciUserspace(SysPciUserspace):
        def devices(self):
            return [TestSysPciUserspaceDevice('slot')]

        def exposed_devices(self):
            return [TestSysPciUserspaceDevice('slot')]

    class TestSysPciUserspaceDevice(SysPciUserspaceDevice):
        def __init__(self, pci_slot, pci_vid=0, pci_did=0,
                     driver='none', owner='nobody', info_string='No info'):
            self.pci_slot = pci_slot
            self.pci_vid = pci_vid
            self.pci_did = pci_did
            self.driver = driver
            self.owner = owner
            self.info_string = info_string

        def pci_regs(self):
            return mocked_pci_regs

        def nvme_regs(self):
            return mocked_nvme_regs

        def map_dma_region_read(self, vaddr, iova, size):
            pass

        def map_dma_region_write(self, vaddr, iova, size):
            pass

        def map_dma_region_rw(self, vaddr, iova, size):
            pass

        def unmap_dma_region(self, iova, size):
            pass

        def reset(self):
            pass

    from stdk.system import MemoryLocation, Memory

    class TestMemory(Memory):
        def __init__(self):
            pass

        def malloc(self, size, align=os.sysconf('SC_PAGE_SIZE')):
            return MemoryLocation(0, size, align)

        def free(self, memory):
            pass

        def get(self, vaddr):
            pass

        def free_all(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            pass

    # Now import the System module and change it's properties to to the test typea above
    from stdk.system import System

    saved_requirements = System.Requirements
    saved_pci = System.Pci
    saved_pci_device = System.PciDevice
    saved_pci_userspace = System.PciUserspace
    saved_pci_userspace_device = System.PciUserspaceDevice
    saved_mem_mgr = System.MemoryMgr

    System.Requirements = TestSysRequirements
    System.Pci = TestSysPci
    System.PciDevice = TestSysPciDevice
    System.PciUserspace = TestSysPciUserspace
    System.PciUserspaceDevice = TestSysPciUserspaceDevice
    System.MemoryMgr = TestMemory

    yield System

    # Revert back to the original System after testing
    System.Requirements = saved_requirements
    System.Pci = saved_pci
    System.PciDevice = saved_pci_device
    System.PciUserspace = saved_pci_userspace
    System.PciUserspaceDevice = saved_pci_userspace_device
    System.MemoryMgr = saved_mem_mgr
