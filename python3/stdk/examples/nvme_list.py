import sys

# Import System Interface class
from stdk.system import System

# Import the demo Driver from examples
from stdk.examples.nvme_demo_driver import NVMeDemoDriver

# Import NVMe device
from stdk.nvme.device import NVMeDevice


def main():
    # Create a memory manager object
    mem_mgr = System.MemoryMgr()

    # Copy the output of nvme-cli's list command
    fmt = '{:<16} {:<20} {:<40} {:<9} {:<26} {:<16} {:<8}'
    print(fmt.format('Node', 'SN', 'Model', 'Namespace', 'Usage', 'Format', 'FW Rev'))
    print(fmt.format('-' * 16, '-' * 20, '-' * 40, '-' * 9, '-' * 26, '-' * 16, '-' * 8))

    # One of the system's interfaces is the current OS's view of all exposed devices we
    #   can work with. Use that interface and list them all
    for device in System.PciUserspace().exposed_devices():
        # Pci slot
        pci_slot = device.pci_slot

        # We are using the NVMeDemoDriver for this right now. It is a simple driver that
        #   allows us to send commands to and get responses from a device. This is not a full
        #   function driver, but good enough for a demo
        nvme_device = NVMeDevice(pci_slot)
        stdk_demo_driver = NVMeDemoDriver(nvme_device, mem_mgr)

        # Set admin queues, re-enable
        stdk_demo_driver.cc_disable()
        stdk_demo_driver.init_admin_queues(asq_entries=16, acq_entries=16)
        stdk_demo_driver.cc_enable()
        stdk_demo_driver.get_namespace_info()

        for ns_id, ns in enumerate(nvme_device.namespaces):
            if ns:
                # Print the information for this device and namespace
                print(fmt.format(pci_slot,
                                 nvme_device.identify_controller_data.SN.strip().decode(),
                                 nvme_device.identify_controller_data.MN.strip().decode(),
                                 ns_id,
                                 '{:>6} {} / {:>6} {}'.format(ns.ns_usage,
                                                              ns.ns_unit,
                                                              ns.ns_total,
                                                              ns.ns_unit),
                                 '{:>3} {:>4} + {} B'.format(ns.lba_size,
                                                             ns.lba_unit,
                                                             ns.ms_bytes),
                                 nvme_device.identify_controller_data.FR.strip().decode()))


if __name__ == '__main__':
    sys.exit(main())
