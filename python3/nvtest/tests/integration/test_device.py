import pytest
import time
from types import SimpleNamespace

from lone.injection import Injector
from lone.system import DMADirection, MemoryLocation
from lone.nvme.device import NVMeDevice, NVMeDeviceCommon
from lone.nvme.spec.structures import ADMINCommand, DataInCommon, DataOutCommon, CQE
from lone.nvme.spec.commands.admin.identify import IdentifyController
from lone.nvme.spec.commands.admin.format_nvm import FormatNVM
from lone.nvme.spec.commands.nvm.write import Write
from lone.nvme.spec.commands.nvm.read import Read
from lone.nvme.spec.commands.status_codes import status_codes


class IgnoreNVMeRegChanges(Injector):
    ''' Injector that should result in the device ignoring all changes to NVMe
        registers for timeout_s seconds. This is helpfull for testing error and
        timeout paths
    '''


class FailCommand(Injector):
    ''' Injector that should result in the device failing the next command we
        send to it
    '''


class SetCFS(Injector):
    ''' Injector that should result in the device setting the CSTS.CFS bit
    '''


def test_cid_mgr(nvme_device_raw):
    cid_mgr = NVMeDeviceCommon.CidMgr(0, 100)
    for i in range(99):
        cid_mgr.get()
    assert cid_mgr.get() == 99
    assert cid_mgr.get() == 0
    assert cid_mgr.get() == 1


def test_device_init(nvme_device):
    assert hasattr(nvme_device, 'pcie_regs')
    assert hasattr(nvme_device, 'nvme_regs')
    assert hasattr(nvme_device, 'cid_mgr')
    assert hasattr(nvme_device, 'queue_mgr')
    assert hasattr(nvme_device, 'mps')
    assert type(nvme_device.mps) is int
    assert hasattr(nvme_device, 'outstanding_commands')
    assert hasattr(nvme_device, 'injectors')


def test_cc_disable(nvme_device_raw):
    nvme_device_raw.cc_disable()
    assert nvme_device_raw.nvme_regs.CSTS.RDY == 0

    # Test the timeout path of disabling with the injector
    #   This only works on the simulator for now, so skip everywhere else
    if nvme_device_raw.pci_slot == 'nvsim':
        # First disable so we are at a known state
        nvme_device_raw.cc_disable()
        nvme_device_raw.init_admin_queues()
        nvme_device_raw.cc_enable(timeout_s=5)

        # Now tell the device to stop listening to CC.EN transitions
        injector = IgnoreNVMeRegChanges(timeout_s=0.1)
        nvme_device_raw.injectors.register(injector)
        injector.wait(1)

        # At this point the device is primed to ignore NVMe register changes for 1s
        with pytest.raises(AssertionError):
            nvme_device_raw.cc_disable(timeout_s=0.01)

    # Test the CFS while disabling path
    #   This only works on the simulator for now, so skip everywhere else
    if nvme_device_raw.pci_slot == 'nvsim':
        # First disable so we are at a known state
        nvme_device_raw.cc_disable()
        nvme_device_raw.init_admin_queues()
        nvme_device_raw.cc_enable(timeout_s=5)

        # Now tell the device to stop listening to CC.EN transitions
        injector = SetCFS(timeout_s=0.1)
        nvme_device_raw.injectors.register(injector)
        injector.wait(1)
        nvme_device_raw.cc_disable()


def test_cc_enable(nvme_device_raw):
    nvme_device_raw.init_admin_queues(asq_entries=16, acq_entries=16)
    nvme_device_raw.cc_enable(timeout_s=5)
    assert nvme_device_raw.nvme_regs.CSTS.RDY == 1

    # Test the timeout path of enabling with the injector
    #   This only works on the simulator for now, so skip everywhere else
    if nvme_device_raw.pci_slot == 'nvsim':
        # First disable so we are at a known state
        nvme_device_raw.cc_disable()

        # Now tell the device to stop listening to CC.EN transitions
        injector = IgnoreNVMeRegChanges(timeout_s=0.1)
        nvme_device_raw.injectors.register(injector)
        injector.wait(1)

        # At this point the device is primed to ignore NVMe register changes for 1s
        with pytest.raises(AssertionError):
            nvme_device_raw.cc_enable(timeout_s=0.01)


def test_init_admin_queues(nvme_device_raw):
    nvme_device_raw.init_admin_queues(asq_entries=16, acq_entries=16)
    assert nvme_device_raw.nvme_regs.ASQ.ASQB != 0
    assert nvme_device_raw.nvme_regs.AQA.ASQS == (16 - 1)
    assert nvme_device_raw.nvme_regs.ACQ.ACQB != 0
    assert nvme_device_raw.nvme_regs.AQA.ACQS == (16 - 1)
    assert len(nvme_device_raw.queue_mgr.nvme_queues) == 1

    # Test CSS != 0x40 path
    nvme_device_raw.nvme_regs.CAP.CSS = 0x00
    nvme_device_raw.init_admin_queues(asq_entries=16, acq_entries=16)


def test_init_io_queues(nvme_device_raw):
    test_init_admin_queues(nvme_device_raw)
    nvme_device_raw.cc_enable()
    nvme_device_raw.init_io_queues()


def test_free_io_queues(nvme_device_raw):
    test_init_admin_queues(nvme_device_raw)
    nvme_device_raw.cc_enable()
    nvme_device_raw.init_io_queues()
    nvme_device_raw.free_io_queues()


def test_ns_size(nvme_device_raw):
    usage, total, unit = NVMeDeviceCommon.ns_size(None, 512, 1, 1)
    assert usage == 512.0 and total == 512.0 and unit == 'B'
    usage, total, unit = NVMeDeviceCommon.ns_size(None, 512, 2, 1)
    assert usage == 0.51 and total == 1.02 and unit == 'KB'
    usage, total, unit = NVMeDeviceCommon.ns_size(None, 512, 2048, 1)
    assert usage == 0.0 and total == 1.05 and unit == 'MB'
    usage, total, unit = NVMeDeviceCommon.ns_size(None, 512, 1024 * 2048, 1)
    assert usage == 0.0 and total == 1.07 and unit == 'GB'
    usage, total, unit = NVMeDeviceCommon.ns_size(None, 512, 1024 * 1024 * 2048, 1)
    assert usage == 0.0 and total == 1.1 and unit == 'TB'


def test_lba_ds_size(nvme_device_raw):
    size, unit = NVMeDeviceCommon.lba_ds_size(None, 512)
    assert size == 512 and unit == 'B'

    size, unit = NVMeDeviceCommon.lba_ds_size(None, 4096)
    assert size == 4 and unit == 'KiB'

    size, unit = NVMeDeviceCommon.lba_ds_size(None, 16384)
    assert size == 16 and unit == 'KiB'


def test_ns_uuid(nvme_device):
    # Test success path
    nvme_device.identify_uuid_list()

    # Test failure path, only nvsim supports injectors for now
    if nvme_device.pci_slot == 'nvsim':
        injector = FailCommand(sc=status_codes['Invalid Field in Command'])
        nvme_device.injectors.register(injector)
        injector.wait(1)
        nvme_device.identify_uuid_list()


def test_identify(nvme_device):
    nvme_device.identify()


def test_post_command(nvme_device):
    pass


def test_process_completions(nvme_device):
    c = nvme_device.process_completions()
    # Nothing to complete, should return 0 completions
    assert c == 0

    c = nvme_device.process_completions(0)
    # Nothing to complete, should return 0 completions
    assert c == 0

    c = nvme_device.process_completions([0, 1])
    # Nothing to complete, should return 0 completions
    assert c == 0


def test_get_completion(nvme_device, mocker):
    assert nvme_device.get_completion(0) is False

    # Test path when we get a completion, but it is not for an outstanding command
    mocked_cqe = CQE()
    mocked_cq = SimpleNamespace(get_next_completion=lambda: mocked_cqe, phase=0)
    mocker.patch('lone.nvme.spec.queues.QueueMgr.get', return_value=(None, mocked_cq))
    with pytest.raises(AssertionError):
        nvme_device.get_completion(0)

    # Test path when we get a completion, but it is not for an outstanding command
    #  when there are multiple outstanding commands with the drive
    mocked_cqe = CQE()
    mocked_cq = SimpleNamespace(get_next_completion=lambda: mocked_cqe, phase=0)
    mocker.patch('lone.nvme.spec.queues.QueueMgr.get', return_value=(None, mocked_cq))
    nvme_device.outstanding_commands = [ADMINCommand(), ADMINCommand()]
    with pytest.raises(AssertionError):
        nvme_device.get_completion(0)

    # Test path when we get a completion, for a command that is outstanding, with memory
    mocked_cqe = CQE()
    mocked_cqe.CID = 0
    mocked_cqe.qid = 0
    mocked_cq = SimpleNamespace(get_next_completion=lambda: mocked_cqe, phase=0,
                                consume_completion=lambda: None)
    mocker.patch('lone.nvme.spec.queues.QueueMgr.get', return_value=(None, mocked_cq))
    nvme_device.outstanding_commands = [ADMINCommand()]
    nvme_device.outstanding_commands[0].posted = True
    nvme_device.outstanding_commands[0].CID = 0
    nvme_device.outstanding_commands[0].internal_mem = True
    nvme_device.outstanding_commands[0].sq = SimpleNamespace(
        qid=0,
        head=SimpleNamespace(set=lambda x: None))
    nvme_device.get_completion(0)

    # Test path when we get a completion, for a command that is outstanding, without memory
    mocked_cqe = CQE()
    mocked_cqe.CID = 0
    mocked_cqe.qid = 0
    mocked_cq = SimpleNamespace(get_next_completion=lambda: mocked_cqe, phase=0,
                                consume_completion=lambda: None)
    mocker.patch('lone.nvme.spec.queues.QueueMgr.get', return_value=(None, mocked_cq))
    nvme_device.outstanding_commands = [ADMINCommand()]
    nvme_device.outstanding_commands[0].posted = True
    nvme_device.outstanding_commands[0].CID = 0
    nvme_device.outstanding_commands[0].internal_mem = False
    nvme_device.outstanding_commands[0].sq = SimpleNamespace(
        qid=0,
        head=SimpleNamespace(set=lambda x: None))
    nvme_device.get_completion(0)


def test_sync_cmd(nvme_device):
    # Replace start_cmd and process_completions with our own stubs
    #  so that we can test the sync_cmd functionality and not worry
    #  about the simulator responding to commands
    nvme_device.process_completions = lambda x, y, z: None
    nvme_device.start_cmd = lambda a, b, c, d: None

    # Create a command to test sync_cmd with
    id_cmd = IdentifyController()
    id_cmd.complete = True
    id_cmd.cq = SimpleNamespace(qid=0)

    # Test path where the command succeeds
    nvme_device.sync_cmd(id_cmd, check=True)
    nvme_device.free_cmd_memory(id_cmd)

    # Test path where the command does not complete
    id_cmd.complete = False
    with pytest.raises(AssertionError):
        nvme_device.sync_cmd(id_cmd, check=True)
    nvme_device.free_cmd_memory(id_cmd)

    # Test path without complete check
    id_cmd.complete = True
    nvme_device.sync_cmd(id_cmd, check=False)
    nvme_device.free_cmd_memory(id_cmd)


def test_start_cmd_admin(lone_config, nvme_device):

    # Get configuration from lone_config, check for required params
    assert len(lone_config['dut']['namespaces']), 'Test requires a namespace'
    test_nsid = lone_config['dut']['namespaces'][0]['nsid']

    # Test path where sending a command that is already with the drive
    #  causes an assert
    id_cmd = IdentifyController()
    nvme_device.start_cmd(id_cmd, sqid=0)
    with pytest.raises(AssertionError):
        nvme_device.start_cmd(id_cmd)

    # Wait for the command to complete
    while id_cmd.complete is False:
        nvme_device.process_completions(max_completions=1)
        time.sleep(0.01)

    # Test start_cmd without allocating memory
    fmt_cmd = FormatNVM(NSID=test_nsid)
    nvme_device.start_cmd(fmt_cmd, alloc_mem=False)

    # Wait for the command to complete
    while fmt_cmd.complete is False:
        nvme_device.process_completions()
        time.sleep(0.01)


def test_start_cmd_nvm(lone_config, nvme_device):

    # Get configuration from lone_config, check for required params
    assert len(lone_config['dut']['namespaces']), 'Test requires a namespace'
    test_nsid = lone_config['dut']['namespaces'][0]['nsid']

    # Test a non admin commands, write first
    wr_cmd = Write(NSID=test_nsid)
    nvme_device.start_cmd(wr_cmd)
    while wr_cmd.complete is False:
        nvme_device.process_completions(max_completions=1)
        time.sleep(0.01)

    # Test Read
    rd_cmd = Read(NSID=test_nsid)
    nvme_device.start_cmd(rd_cmd)
    while rd_cmd.complete is False:
        nvme_device.process_completions(max_completions=1)
        time.sleep(0.01)


def test_alloc_cmd_memory(lone_config, nvme_device):

    # Get configuration from lone_config, check for required params
    assert len(lone_config['dut']['namespaces']), 'Test requires a namespace'
    test_nsid = lone_config['dut']['namespaces'][0]['nsid']

    cmd = ADMINCommand()
    cmd.data_in = DataInCommon()
    cmd.data_in.size = 4096
    cmd.data_out = DataOutCommon()
    cmd.data_out.size = 4096
    with pytest.raises(AssertionError):
        nvme_device.alloc_cmd_memory(cmd)
    nvme_device.free_cmd_memory(cmd)

    cmd = Write(NSID=test_nsid)
    nvme_device.alloc_cmd_memory(cmd)
    nvme_device.free_cmd_memory(cmd)

    cmd = Read(NSID=test_nsid)
    nvme_device.alloc_cmd_memory(cmd)
    nvme_device.free_cmd_memory(cmd)

    cmd = IdentifyController()
    nvme_device.alloc_cmd_memory(cmd)
    nvme_device.free_cmd_memory(cmd)

    cmd = ADMINCommand()
    cmd.data_out = DataOutCommon()
    cmd.data_out.size = 4096
    nvme_device.alloc_cmd_memory(cmd)
    nvme_device.free_cmd_memory(cmd)

    cmd = ADMINCommand()
    cmd.data_out = DataOutCommon()
    cmd.data_out.size = 4096
    nvme_device.alloc_cmd_memory(cmd)
    nvme_device.free_cmd_memory(cmd)


def test_mocked_physical_device(mocker):
    ''' Test a heavily mocked version of a physical PCIe device
    '''
    mocked_pcie_regs = SimpleNamespace(init_capabilities=lambda: None)
    mocked_nvme_regs = SimpleNamespace(CC=SimpleNamespace(MPS=4096))
    mocked_system = SimpleNamespace(pci_regs=lambda: mocked_pcie_regs,
                                    nvme_regs=lambda: mocked_nvme_regs,
                                    map_dma_region_read=lambda x, y, z: None,
                                    map_dma_region_write=lambda x, y, z: None,
                                    unmap_dma_region=lambda x, y: None)
    mocker.patch('lone.system.System.PciUserspaceDevice', return_value=mocked_system)
    mocked_mem_mgr = SimpleNamespace(malloc=lambda x, client: MemoryLocation(0, 0, 0, 0, 'test'),
                                     free=lambda x: None)
    mocker.patch('lone.system.System.MemoryMgr', return_value=mocked_mem_mgr)
    phys_dev = NVMeDevice('mocked_slot')

    # Test malloc_and_map_iova
    phys_dev.malloc_and_map_iova(4096, DMADirection.HOST_TO_DEVICE)
    phys_dev.malloc_and_map_iova(4096, DMADirection.DEVICE_TO_HOST)
    with pytest.raises(AssertionError):
        phys_dev.malloc_and_map_iova(4096, DMADirection.BIDIRECTIONAL)

    # Test free_and_unmap_iova
    mem = MemoryLocation(0, 0, 0, 0, 'test')
    phys_dev.free_and_unmap_iova(mem)
