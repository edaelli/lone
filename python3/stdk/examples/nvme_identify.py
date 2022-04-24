import sys
import argparse

# Import stdk StructFieldsIterator which helps printing out ctypes.Structs
from stdk.util.struct_tools import StructFieldsIterator

# Import System Interface class. This is how we get the MemoryMgr object for
#   the running system
from stdk.system import System

# Import the demo Driver from examples. This is a simple driver that allows
#   us to setup a device and send/receive commands
from stdk.examples.nvme_demo_driver import NVMeDemoDriver

# Import NVMe device. This gets us (and the driver) access to the device's
#   PCIe and NVMe registers
from stdk.nvme.device import NVMeDevice

# Import NVMe spec objects we will use for commands
from stdk.nvme.spec.commands.admin.identify import IdentifyController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pci_slot', type=str)
    args = parser.parse_args()

    # Create a memory manager object
    mem_mgr = System.MemoryMgr()

    # Create a NVMeDevice object for the slot we want to work with
    nvme_device = NVMeDevice(args.pci_slot)

    # Use the NVMeDemoDriver for examples
    stdk_demo_driver = NVMeDemoDriver(nvme_device, mem_mgr)

    # Disable, set admin queues, re-enable
    stdk_demo_driver.cc_disable()
    stdk_demo_driver.init_admin_queues(asq_entries=16, acq_entries=16)
    stdk_demo_driver.cc_enable()
    stdk_demo_driver.init_io_queues(1, 16)

    # Send an Identify controller command, check response
    id_ctrl_cmd = IdentifyController()
    cqe = stdk_demo_driver.sync_cmd(id_ctrl_cmd)
    assert cqe.SF.SC == 0, 'Command failed with SF.SC = 0x{:x}'.format(cqe.SF.SC)

    # Print all the data in the response using the StructFieldsIterator
    for field, value in StructFieldsIterator(id_ctrl_cmd.data_in):

        # Don't print reserved (or not yet defined) values
        if 'RSVD' not in field and 'TBD' not in field:
            # Decode and print bytes as strings
            if type(value) == bytes:
                fmt = '{:40} {}'
                value = value.decode()

            # Print ints as hex
            if type(value) == int:
                fmt = '{:40} 0x{:x}'

            print(fmt.format(field, value))


if __name__ == '__main__':
    sys.exit(main())
