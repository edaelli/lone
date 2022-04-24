import pytest

from types import SimpleNamespace


def test_linux_sys_pci(mocker):
    from stdk.system.linux.pci import LinuxSysPci
    sys_pci = LinuxSysPci()

    mocker.patch('builtins.open', mocker.mock_open(read_data='0'))
    sys_pci.rescan()


def test_linux_sys_pci_device(mocker):
    from stdk.system.linux.pci import LinuxSysPciDevice
    mocker.patch('os.readlink', return_value='')
    sys_pci_dev = LinuxSysPciDevice('')

    mocker.patch('os.path.exists', return_value=False)
    sys_pci_dev.exists()

    mocker.patch('os.path.exists', return_value=False)
    sys_pci_dev.remove()
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data='0'))
    sys_pci_dev.remove()

    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('pwd.getpwnam', return_value=SimpleNamespace(pw_uid=1000, pw_gid=1000))
    mocker.patch('pwd.getpwuid', return_value=SimpleNamespace(pw_uid=1000, pw_gid=1000))
    mocker.patch('os.chown', return_value=True)
    mocker.patch('os.stat', return_value=SimpleNamespace(st_uid=1000, st_gid=1000))
    mocker.patch('subprocess.check_output', return_value=b'00:00.0 0000 1234:5678')

    sys_pci_dev.expose('user')
    sys_pci_dev.expose('1000')
    sys_pci_dev.expose(1000)

    mocker.patch('os.path.exists', return_value=False)
    sys_pci_dev.reclaim('driver')

    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.basename', return_value='test')
    sys_pci_dev._unbind_current_driver()

    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.basename', return_value='vfio_pci')
    sys_pci_dev._unbind_current_driver()

    mocker.patch('os.path.exists', return_value=False)
    sys_pci_dev._bind_to_driver('driver')

    mocker.patch('os.path.exists', return_value=True)
    sys_pci_dev._bind_to_driver('driver')

    mocker.patch('os.path.exists', return_value=True)
    sys_pci_dev._create_device()

    sys_pci_dev._change_device_ownership('path', 'owner')
    sys_pci_dev._change_device_ownership('path', 1000)
    with pytest.raises(Exception):
        sys_pci_dev._change_device_ownership('path', [])
