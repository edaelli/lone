import sys
import argparse
import ctypes
import random

# Import stdk StructFieldsIterator which helps printing out ctypes.Structs
from stdk.util.hexdump import hexdump_print

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
from stdk.nvme.spec.commands.nvm.read import Read
from stdk.nvme.spec.commands.nvm.write import Write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pci_slot', type=str)
    parser.add_argument('namespace', type=int)
    args = parser.parse_args()

    # Create a memory manager object
    mem_mgr = System.MemoryMgr()

    # Create a NVMeDevice object for the slot we want to work with
    nvme_device = NVMeDevice(args.pci_slot)

    # Use the NVMeDemoDriver for examples
    stdk_demo_driver = NVMeDemoDriver(nvme_device, mem_mgr)

    # Disable, create queues, get namespace information
    stdk_demo_driver.cc_disable()
    stdk_demo_driver.init_admin_queues(asq_entries=16, acq_entries=16)
    stdk_demo_driver.cc_enable()
    stdk_demo_driver.init_io_queues(1, 16)
    stdk_demo_driver.get_namespace_info()

    # Get the namespace's information (which is filled in by get_namespace_info)
    ns = nvme_device.namespaces[args.namespace]
    ns_block_size = ns.lba_ds_bytes

    # Random IOVA start address
    iova = 0xA0000000

    # Random seed for repeatability
    random.seed(237)

    # Allocate memory, map it with the device, and use it for a write command
    write_mem = mem_mgr.malloc(ns_block_size)
    write_mem.iova = iova
    iova += write_mem.size
    nvme_device.map_dma_region_read(write_mem.vaddr, write_mem.iova, write_mem.size)

    # Fill the write buffer with seeded random data
    rand_data = ctypes.create_string_buffer(
        bytes([random.randint(0, 0xFF) for i in range(ns_block_size - 1)]))
    ctypes.memmove(write_mem.vaddr, ctypes.addressof(rand_data), write_mem.size)

    # Create the write command pointing to our data buffer
    write_cmd = Write(NSID=args.namespace, SLBA=0, NLB=0)
    write_cmd.DPTR.PRP.PRP1 = write_mem.iova

    # Dump the first 256 bytes of data
    print('Write data[:256]:')
    hexdump_print(rand_data[:256])
    print()

    # Send the write command, wait for the response
    cqe = stdk_demo_driver.sync_cmd(write_cmd)
    assert cqe.SF.SC == 0, 'Command failed with SF.SC = 0x{:x}'.format(cqe.SF.SC)

    # Write command complete, allocate and map memory for a read to verify it
    read_mem = mem_mgr.malloc(ns_block_size)
    read_mem.iova = iova
    iova += read_mem.size
    nvme_device.map_dma_region_write(read_mem.vaddr, read_mem.iova, read_mem.size)

    # Create the read command pointing to our data buffer
    read_cmd = Read(NSID=args.namespace, SLBA=0, NLB=0)
    read_cmd.DPTR.PRP.PRP1 = read_mem.iova

    # Send the read command, wait for the response
    cqe = stdk_demo_driver.sync_cmd(read_cmd)
    assert cqe.SF.SC == 0, 'Command failed with SF.SC = 0x{:x}'.format(cqe.SF.SC)

    # Read command complete, dump the first 256 bytes of read data
    print('Read data[:256]:')
    read_data = ctypes.create_string_buffer(read_mem.size)
    ctypes.memmove(ctypes.addressof(read_data), read_mem.vaddr, read_mem.size)
    hexdump_print(read_data[:256])

    # Compare the written to read data and verify they match!
    for i, value in enumerate(rand_data):
        assert value == read_data[i], 'Mismatch at byte {}: {} != {}'.format(i, value, read_data[i])


if __name__ == '__main__':
    sys.exit(main())
