import pytest
import os
import importlib.util


def test_system_picker(mocker):
    mocker.patch('platform.system', return_value='Linux')
    file_path = os.path.abspath(os.path.join(__file__, '../../../../stdk/system/__init__.py'))
    spec = importlib.util.spec_from_file_location('test.system', file_path)
    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)

    mocker.patch('platform.system', return_value='test_system')
    spec = importlib.util.spec_from_file_location('test.system', file_path)
    test_module = importlib.util.module_from_spec(spec)
    with pytest.raises(NotImplementedError):
        spec.loader.exec_module(test_module)


def test_no_mem_mgr(mocker, mocked_system):
    mocker.patch('platform.system', return_value='Linux')

    def init(self):
        raise ModuleNotFoundError

    mocker.patch('stdk.system.linux.hugepages.HugePagesMemory.__init__', init)

    file_path = os.path.abspath(os.path.join(__file__, '../../../../stdk/system/__init__.py'))
    spec = importlib.util.spec_from_file_location('test.system', file_path)
    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)

    pass


def test_system_interface(mocker):

    from stdk.system import SysRequirements
    mocker.patch("stdk.system.SysRequirements.__abstractmethods__", set())
    reqs = SysRequirements()
    with pytest.raises(NotImplementedError):
        reqs.check_requirements()

    from stdk.system import SysPci
    mocker.patch("stdk.system.SysPci.__abstractmethods__", set())
    sys_pci = SysPci()
    with pytest.raises(NotImplementedError):
        sys_pci.rescan()

    from stdk.system import SysPciDevice
    mocker.patch("stdk.system.SysPciDevice.__abstractmethods__", set())
    sys_pci_dev = SysPciDevice('pci_slot')
    with pytest.raises(NotImplementedError):
        sys_pci_dev.exists()
    with pytest.raises(NotImplementedError):
        sys_pci_dev.remove()
    with pytest.raises(NotImplementedError):
        sys_pci_dev.expose('user')
    with pytest.raises(NotImplementedError):
        sys_pci_dev.reclaim('driver')

    from stdk.system import SysPciUserspace
    mocker.patch("stdk.system.SysPciUserspace.__abstractmethods__", set())
    sys_pci_userspace = SysPciUserspace()
    with pytest.raises(NotImplementedError):
        sys_pci_userspace.devices()
    with pytest.raises(NotImplementedError):
        sys_pci_userspace.exposed_devices()

    from stdk.system import SysPciUserspaceDevice
    mocker.patch("stdk.system.SysPciUserspaceDevice.__abstractmethods__", set())
    sys_pci_userspace_dev = SysPciUserspaceDevice('pci_slot')
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.pci_regs()
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.nvme_regs()
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.map_dma_region_read(0, 0, 0)
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.map_dma_region_write(0, 0, 0)
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.map_dma_region_rw(0, 0, 0)
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.unmap_dma_region(0, 0)
    with pytest.raises(NotImplementedError):
        sys_pci_userspace_dev.reset()

    from stdk.system import MemoryLocation
    mem = MemoryLocation(0, 0, 0)
    mem

    from stdk.system import Memory
    mocker.patch("stdk.system.Memory.__abstractmethods__", set())
    with Memory() as mem_mgr:
        with pytest.raises(NotImplementedError):
            mem_mgr.malloc(0)
        with pytest.raises(NotImplementedError):
            mem_mgr.free(0)
        mem_mgr.free_all()

        mem_mgr.allocated_mem_addrs.append(MemoryLocation(0, 0, 0))
        mem_mgr.get(0)
        mem_mgr.allocated_mem_addrs.append(MemoryLocation(0, 0, 0))
        mem_mgr.get(1)

        with pytest.raises(NotImplementedError):
            mem_mgr.free_all()
