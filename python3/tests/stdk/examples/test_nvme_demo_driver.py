import pytest
from types import SimpleNamespace

from stdk.examples.nvme_demo_driver import NVMeDemoDriver
from stdk.nvme.spec.structures import CQE
from stdk.nvme.spec.commands.admin.identify import (IdentifyNamespace,
                                                    IdentifyNamespaceList)


def test_demo_driver(mocker, mocked_system, mocked_nvme_device, mocked_nvme_command):
    # Create the device and demo driver objects
    nvme_device = mocked_nvme_device('pci_slot')
    driver = NVMeDemoDriver(nvme_device, mocked_system.MemoryMgr())

    # Mock memmove and from_address calls
    mocker.patch('ctypes.memmove', return_value=None)
    cqe = CQE()
    mocker.patch('stdk.nvme.spec.structures.CQE.from_address', return_value=cqe)

    # Test successful disable
    nvme_device.nvme_regs.CC.EN = 1
    nvme_device.nvme_regs.CSTS.RDY = 0
    driver.cc_disable()
    assert nvme_device.nvme_regs.CC.EN == 0

    # Test disable timeout
    with pytest.raises(AssertionError):
        nvme_device.nvme_regs.CC.EN = 1
        nvme_device.nvme_regs.CSTS.RDY = 1
        driver.cc_disable(timeout_s=0.001)
        assert nvme_device.nvme_regs.CC.EN == 1

    # Test successful enable
    nvme_device.nvme_regs.CC.EN = 0
    nvme_device.nvme_regs.CSTS.RDY = 1
    driver.cc_enable()
    assert nvme_device.nvme_regs.CC.EN == 1

    # Test disable timeout
    with pytest.raises(AssertionError):
        nvme_device.nvme_regs.CC.EN = 0
        nvme_device.nvme_regs.CSTS.RDY = 0
        driver.cc_enable(timeout_s=0.001)
        assert nvme_device.nvme_regs.CC.EN == 0

    # Test init_admin_queues
    driver.init_admin_queues(64, 64)
    cqe.SF.P = 1
    driver.init_io_queues(10, 10)

    # Command with data in that does not timeout
    cqe.SF.P = 1
    nvme_command = mocked_nvme_command()
    mocker.patch.object(nvme_command, 'cmdset_admin', True)
    driver.sync_cmd(nvme_command)

    cqe.SF.P = 1
    nvme_command = mocked_nvme_command()
    mocker.patch.object(nvme_command, 'cmdset_admin', False)
    driver.sync_cmd(nvme_command)

    # Command with data in that does timeout
    cqe = CQE()
    cqe.SF.P = 0
    mocker.patch('stdk.nvme.spec.structures.CQE.from_address', return_value=cqe)
    with pytest.raises(AssertionError):
        driver.sync_cmd(nvme_command, timeout_s=0.001)

    # Command without data in
    cqe = CQE()
    cqe.SF.P = 1
    nvme_command.data_in.size = 0
    mocker.patch('stdk.nvme.spec.structures.CQE.from_address', return_value=cqe)
    driver.sync_cmd(nvme_command)

    # Test queue code
    mem = mocked_system.MemoryMgr().malloc(4096)
    q = NVMeDemoDriver.NVMeQueue(mem, 1024, 16)
    assert q.get_next_available_slot() == (1, 0)
    assert q.get_next_available_slot() == (2, 16)

    # Test wrapping
    q.current_slot = 1023
    assert q.get_next_available_slot() == (0, 16368)


def test_get_namespace_info(mocker, mocked_system, mocked_nvme_device):
    # Mock memmove and from_address calls
    mocker.patch('ctypes.memmove', return_value=None)
    cqe = CQE()
    mocker.patch('stdk.nvme.spec.structures.CQE.from_address', return_value=cqe)

    mem = mocked_system.MemoryMgr()
    device = mocked_nvme_device('test_device')

    driver = NVMeDemoDriver(device, mem)
    q = NVMeDemoDriver.NVMeQueue(mem.malloc(4096), 1024, 16)
    driver.nvme_queues[0] = (q, q)

    def data_in(driver, command, timeout=None):
        cqe.SF.P = 1
        if type(command) == IdentifyNamespaceList:
            identifiers = [1] + ([0] * 1023)
            command.data_in = SimpleNamespace(Identifiers=identifiers)
        elif type(command) == IdentifyNamespace:
            command.data_in = SimpleNamespace(NSZE=0, NUSE=0, FLBAS=1,
                                              LBAF_TBL=[0, SimpleNamespace(LBADS=1, MS=0)])
        return cqe
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.sync_cmd', data_in)

    driver.get_namespace_info()


def test_ns_size(mocked_system, mocked_nvme_device):
    mem = mocked_system.MemoryMgr()
    device = mocked_nvme_device('test_device')
    driver = NVMeDemoDriver(device, mem)

    usage, total, unit = driver.ns_size(1, 1, 1)
    assert (usage, total, unit) == (1, 1, 'B')

    usage, total, unit = driver.ns_size(4096, 1, 1)
    assert (usage, total, unit) == (4.1, 4.1, 'KB')

    usage, total, unit = driver.ns_size(4096, 1000, 1000)
    assert (usage, total, unit) == (4.1, 4.1, 'MB')

    usage, total, unit = driver.ns_size(4096, 1000000, 1000000)
    assert (usage, total, unit) == (4.1, 4.1, 'GB')

    usage, total, unit = driver.ns_size(4096, 1000000000, 1000000000)
    assert (usage, total, unit) == (4.1, 4.1, 'TB')

    size, unit = driver.lba_ds_size(1)
    assert (size, unit) == (1, 'B')

    size, unit = driver.lba_ds_size(1025)
    assert (size, unit) == (1, 'KiB')
