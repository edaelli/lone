import os
import pytest
import argparse
import importlib

from stdk.examples.nvme_identify import main
from stdk.nvme.spec.structures import CQE


def test_nvme_identify(mocker, mocked_system):
    mocker.patch('argparse.ArgumentParser.parse_args',
                 return_value=argparse.Namespace(pci_slot=''))
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.cc_disable', lambda x: None)
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.cc_enable', lambda x: None)
    mocker.patch('stdk.examples.nvme_demo_driver.NVMeDemoDriver.sync_cmd',
                 lambda self, command, timeout_s=None: CQE())

    file_path = os.path.abspath(os.path.join(__file__,
                                             '../../../../stdk/examples/nvme_identify.py'))
    spec = importlib.util.spec_from_file_location('__main__', file_path)
    test_module = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit):
        spec.loader.exec_module(test_module)
    main()
