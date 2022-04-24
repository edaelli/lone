import pytest
import subprocess

from stdk.system.linux.requirements import LinuxRequirements


def test_requirements():
    req = LinuxRequirements()

    req.print_status('desc', True)
    req.print_status('desc', False)
    req.print_status('desc', False, extra='extra')


def test_check_requirements():
    req = LinuxRequirements()
    req.check_python = lambda: None
    req.check_ubuntu = lambda: None
    req.check_VT_VI = lambda: None
    req.check_hugepages = lambda: None
    req.check_hugepages_lib = lambda: None

    req.failure = True
    req.check_requirements()

    req.failure = False
    req.check_requirements()


def test_check_python(mocker):
    req = LinuxRequirements()

    mocker.patch('sys.version_info', (3, 0, 0))
    mocker.patch('platform.python_version', return_value='3.0.0')
    req.check_python()

    mocker.patch('sys.version_info', (3, 10, 0))
    mocker.patch('platform.python_version', return_value='3.10.0')
    req.check_python()


def test_check_ubuntu(mocker):
    req = LinuxRequirements()

    output = b'''
        No LSB modules are available.
        Distributor ID: Ubuntu
        Description:    Ubuntu 20.04.4 LTS
        Release:        20.04
        Codename:       focal
    '''
    mocker.patch('subprocess.check_output', return_value=output)
    req.check_ubuntu()

    output = b'''
        No LSB modules are available.
        Distributor ID: Ubuntu
        Description:    Ubuntu 19.04.4 LTS
        Release:        19.04
        Codename:       focal
    '''
    mocker.patch('subprocess.check_output', return_value=output)
    req.check_ubuntu()

    mocker.patch('subprocess.check_output', side_effect=Exception('test'))
    with pytest.raises(Exception):
        req.check_ubuntu()


def test_check_vt_vi(mocker):
    req = LinuxRequirements()

    mocker.patch('subprocess.check_call', return_value='')
    req.check_VT_VI()

    mocker.patch('subprocess.check_call', side_effect=subprocess.CalledProcessError('test', 'cmd'))
    req.check_VT_VI()


def test_hugepages(mocker):
    req = LinuxRequirements()

    data = '''
        HugePages_Total:     128
        HugePages_Free:      128
        HugePages_Rsvd:        0
        HugePages_Surp:        0
        Hugepagesize:       2048 kB
        Hugetlb:          262144 kB
    '''
    mocker.patch('builtins.open', mocker.mock_open(read_data=data))
    req.check_hugepages()


def test_hugepages_lib(mocker):
    req = LinuxRequirements()

    mocker.patch('subprocess.check_call', return_value=0)
    req.check_hugepages_lib()

    mocker.patch('subprocess.check_call', side_effect=subprocess.CalledProcessError('test', 'cmd'))
    req.check_hugepages_lib()
