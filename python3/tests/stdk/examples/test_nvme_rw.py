import os
import pytest
import argparse
import importlib
import ctypes
from types import SimpleNamespace

from stdk.examples.nvme_rw import main
from stdk.nvme.spec.structures import CQE


def test_nvme_rw(mocker, mocked_system, mocked_nvme_device):
    mocker.patch('argparse.ArgumentParser.parse_args',
                 return_value=argparse.Namespace(pci_slot='', namespace=0))
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.cc_disable', lambda x: None)
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.cc_enable', lambda x: None)
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.sync_cmd',
                 lambda self, command, timeout_s=None: CQE())
    mocker.patch('ctypes.memmove', return_value=None)
    mocker.patch('ctypes.create_string_buffer', return_value=ctypes.create_string_buffer(1))

    def get_namespae_info(driver):
        driver.nvme_device.identify_controller_data = SimpleNamespace(SN=b'', MN=b'', FR=b'')
        driver.nvme_device.namespaces = [SimpleNamespace(ns_usage=0, ns_unit='B',
                                                         ns_total=0, lba_size=0, lba_unit='B',
                                                         ms_bytes=0, lba_ds_bytes=4096)]
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.get_namespace_info',
                 get_namespae_info)

    file_path = os.path.abspath(os.path.join(__file__, '../../../../stdk/examples/nvme_rw.py'))
    spec = importlib.util.spec_from_file_location('__main__', file_path)
    test_module = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit):
        spec.loader.exec_module(test_module)
    main()
