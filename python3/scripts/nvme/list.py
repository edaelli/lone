import sys
import argparse
import logging
from types import SimpleNamespace

# lone imports
from lone.system import System
from lone.nvme.device import NVMeDevice
from lone.util.logging import log_format


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Turn on debug logging')
    args = parser.parse_args()

    # Set our global logging config here depending on what the user requested
    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format=log_format)

    # Copy the output of nvme-cli's list command
    fmt = '{:<16} {:<20} {:<40} {:<9} {:<26} {:<16} {:<8}'
    print(fmt.format('Node', 'SN', 'Model', 'Namespace', 'Usage', 'Format', 'FW Rev'))
    print(fmt.format('-' * 16, '-' * 20, '-' * 40, '-' * 9, '-' * 26, '-' * 16, '-' * 8))

    # One of the system's interfaces is the current OS's view of all exposed devices we
    #   can work with. Use that interface and list them all
    for device in [SimpleNamespace(pci_slot='nvsim')] + System.PciUserspace().exposed_devices():
        # Pci slot
        pci_slot = device.pci_slot

        # We are using the NVMeDemoDriver for this right now. It is a simple driver that
        #   allows us to send commands to and get responses from a device. This is not a full
        #   function driver, but good enough for a demo
        nvme_device = NVMeDevice(pci_slot)

        # Set admin queues, re-enable
        nvme_device.cc_disable()
        nvme_device.init_admin_queues(asq_entries=16, acq_entries=16)
        nvme_device.cc_enable()
        nvme_device.identify()
        identify_controller_data = nvme_device.identify_data['controller']

        for ns_id, ns in enumerate(nvme_device.namespaces):
            if ns:
                # Print the information for this device and namespace
                print(fmt.format(pci_slot,
                                 identify_controller_data.SN.strip().decode(),
                                 identify_controller_data.MN.strip().decode(),
                                 ns_id,
                                 '{:>6} {} / {:>6} {}'.format(ns.ns_usage,
                                                              ns.ns_unit,
                                                              ns.ns_total,
                                                              ns.ns_unit),
                                 '{:>3} {:>4} + {} B'.format(ns.lba_size,
                                                             ns.lba_unit,
                                                             ns.ms_bytes),
                                 identify_controller_data.FR.strip().decode()))


if __name__ == '__main__':
    sys.exit(main())
