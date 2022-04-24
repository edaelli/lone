import ctypes
import subprocess

from stdk.system.linux.vfio import VfioIoctl, VfioGetApiVersion
from stdk.system.linux.vfio import SysVfioIfc, SysVfio


def test_vfio_ioctl(mocker):
    vfio_ioctl = VfioIoctl()
    vfio_ioctl

    mocker.patch('ioctl_opt.IO', return_value=0)
    mocker.patch('fcntl.ioctl', return_value=0)

    # Test the VfioIoctl interfaces
    VfioGetApiVersion().ioctl(0)
    VfioGetApiVersion().ioctl(0, 0)
    VfioGetApiVersion().ioctl(0)
    VfioGetApiVersion().get_data()


def test_sysvfioifc_init(mocker):
    # Test interface without init
    ifc = SysVfioIfc('test', init=False)
    assert ifc.pci_slot == 'test'

    # Test interface with init
    mocker.patch('os.open', return_value=0)
    mocker.patch('os.readlink', return_value='')
    mocker.patch('fcntl.ioctl',
                 side_effect=[0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x00] + [0] * 9)
    from stdk.system.linux.vfio import VfioGroupGetStatus, VfioDeviceGetInfo
    mocker.patch('stdk.system.linux.vfio.VfioGroupGetStatus.get_data',
                 side_effect=[VfioGroupGetStatus(flags=0x01), VfioGroupGetStatus(flags=0x03)])
    mocker.patch('stdk.system.linux.vfio.VfioDeviceGetInfo.get_data',
                 side_effect=[VfioDeviceGetInfo(num_regions=9)])
    ifc = SysVfioIfc('test', init=True)


def test_sysvfioifc_pci_regs(mocker):
    ifc = SysVfioIfc('test', init=False)
    ifc.device_fd = 1
    ifc.pci_region = {'size': 0, 'offset': 0}
    ifc.pci_regs()


def test_sysvfioifc_nvme_regs(mocker):
    ifc = SysVfioIfc('test', init=False)
    assert ifc.pci_slot == 'test'
    ifc.device_fd = 1
    ifc.bars = []
    ifc.bars.append({'size': 0, 'offset': 0})
    mocker.patch('mmap.mmap', return_value=(ctypes.c_uint8 * 16 * 1024)())
    ifc.nvme_regs()


def test_sysvfioifc_dma(mocker):
    ifc = SysVfioIfc('test', init=False)
    ifc.container_fd = 1
    mocker.patch('fcntl.ioctl', return_value=0)
    ifc.map_dma_region(0, 0, 0, 0)
    ifc.map_dma_region_read(0, 0, 0)
    ifc.map_dma_region_write(0, 0, 0)
    ifc.map_dma_region_rw(0, 0, 0)
    ifc.unmap_dma_region(0, 0)


def test_sysvfioifc_reset(mocker):
    ifc = SysVfioIfc('test', init=False)
    mocker.patch('fcntl.ioctl', return_value=0)
    ifc.device_fd = 1
    ifc.reset()


def test_sysvfioifc_clean(mocker):
    ifc = SysVfioIfc('test', init=False)
    ifc.container_fd = 1
    ifc.group_fd = 1
    mocker.patch('os.close', return_value=0)
    ifc._clean()


def test_sysvfio_exposed_devices(mocker):
    sysvfio = SysVfio()
    mocker.patch('subprocess.check_output', return_value=b'')
    mocker.patch('pyudev.Context.list_devices', return_value=[])
    sysvfio.exposed_devices()


def test_sysvfio_devices(mocker):
    sysvfio = SysVfio()

    mocker.patch('subprocess.check_output', return_value=b'')
    mocker.patch('pyudev.Context.list_devices', return_value=[])
    sysvfio.devices()

    mocker.patch('pyudev.Context.list_devices', return_value=[{'SUBSYSTEM': 'not_pci'}])
    sysvfio.devices()

    mocker.patch('subprocess.check_output',
                 side_effect=subprocess.CalledProcessError('test', 'cmd'))
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()

    mocker.patch('subprocess.check_output', side_effect=[
        b'/sys/kernel/iommu_groups/17/devices/not_find_name\n',
        b'\n',
        b'\nslot_name: information\n'])
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()

    mocker.patch('subprocess.check_output', side_effect=[
        b'/sys/kernel/iommu_groups/17/devices/slot_name\n',
        b'\n',
        b'\nslot_name: information\n'])
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()

    mocker.patch('subprocess.check_output', side_effect=[
        b'/sys/kernel/iommu_groups/17/devices/slot_name\n',
        b'\n',
        b'\nslot_name: information\n'])
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'DEVNAME': 'test',
                                'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()

    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.readlink', return_value='')
    mocker.patch('subprocess.check_output', side_effect=[
        b'/sys/kernel/iommu_groups/17/devices/slot_name\n',
        b'\n',
        b'\nslot_name: information\n'])
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'DEVNAME': 'test',
                                'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()

    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.readlink', return_value='vfio_pci')
    mocker.patch('pathlib.Path.owner', return_value='owner')
    mocker.patch('subprocess.check_output', side_effect=[
        b'/sys/kernel/iommu_groups/17/devices/slot_name\n',
        b'\n',
        b'\nslot_name: information\n'])
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'DEVNAME': 'test',
                                'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()

    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.readlink', return_value='vfio_pci')
    mocker.patch('pathlib.Path.owner', return_value='owner')
    mocker.patch('subprocess.check_output', side_effect=[
        b'/sys/kernel/iommu_groups/17/devices/slot_name\n',
        b'test\n',
        b'\nslot_name: information\n'])
    mocker.patch('pyudev.Context.list_devices',
                 return_value=[{'DEVNAME': 'test',
                                'SUBSYSTEM': 'pci',
                                'PCI_CLASS': '10802',
                                'PCI_SLOT_NAME': 'slot_name',
                                'PCI_ID': '1:1'}])
    sysvfio.devices()
