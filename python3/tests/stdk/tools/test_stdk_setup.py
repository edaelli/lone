import pytest
import argparse

from stdk.tools import stdk_setup


def test_main_no_option(mocker):
    mocker.patch('argparse.ArgumentParser.parse_known_args',
                 return_value=(argparse.Namespace(action=''),
                               argparse.Namespace()))
    stdk_setup.main()


def test_main_list(mocker, mocked_system):
    mocker.patch('argparse.ArgumentParser.parse_known_args',
                 return_value=(argparse.Namespace(action='list'),
                               argparse.Namespace()))
    # With one device
    dev = mocked_system.PciUserspaceDevice('slot')
    mocker.patch('stdk.tools.stdk_setup.System.PciUserspace.devices', lambda x: [dev])
    stdk_setup.main()

    # With no devices
    mocker.patch('stdk.tools.stdk_setup.System.PciUserspace.devices', lambda x: [])
    stdk_setup.main()


def test_main_req(mocker, mocked_system):
    mocker.patch('argparse.ArgumentParser.parse_known_args',
                 return_value=(argparse.Namespace(action='requirements'),
                               argparse.Namespace()))
    stdk_setup.main()


def test_main_expose(mocker, monkeypatch, mocked_system):
    # Mock going down the expose path
    mocker.patch('argparse.ArgumentParser.parse_known_args',
                 return_value=(argparse.Namespace(action='expose'),
                               argparse.Namespace()))
    mocker.patch('argparse.ArgumentParser.parse_args',
                 return_value=argparse.Namespace(pci_slot='pci_slot', user='user'))

    # Not root
    mocker.patch('os.geteuid', return_value=1)
    with pytest.raises(SystemExit):
        stdk_setup.main()

    # Root, device exists
    mocker.patch('os.geteuid', return_value=0)
    monkeypatch.setattr(mocked_system.PciDevice, 'exists', lambda x: True)
    stdk_setup.main()

    # Root, device does not exist
    mocker.patch('os.geteuid', return_value=0)
    monkeypatch.setattr(mocked_system.PciDevice, 'exists', lambda x: False)
    with pytest.raises(SystemExit):
        stdk_setup.main()


def test_main_reclaim(mocker, mocked_system):
    # Mock going down the reclaim path
    mocker.patch('argparse.ArgumentParser.parse_known_args',
                 return_value=(argparse.Namespace(action='reclaim'),
                               argparse.Namespace()))
    mocker.patch('argparse.ArgumentParser.parse_args',
                 return_value=argparse.Namespace(pci_slot='pci_slot', driver='driver'))

    # Not root
    mocker.patch('os.geteuid', return_value=1)
    with pytest.raises(SystemExit):
        stdk_setup.main()

    # Root, device exists
    mocker.patch('os.geteuid', return_value=0)
    stdk_setup.main()
