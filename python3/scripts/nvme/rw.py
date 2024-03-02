import sys
import argparse
import logging

# Import NVMe device. This gets us (and the driver) access to the device's
#   PCIe and NVMe registers
from lone.nvme.device import NVMeDevice

# Import NVMe spec objects we will use for commands
from lone.nvme.spec.commands.nvm.read import Read
from lone.nvme.spec.commands.nvm.write import Write
from lone.nvme.spec.prp import PRP
from lone.system import DMADirection
from lone.util.logging import log_format


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Turn on debug logging')
    parser.add_argument('pci_slot', type=str)
    parser.add_argument('namespace', type=int)
    parser.add_argument('--slba', type=int, default=0)
    parser.add_argument('--block-size', type=int, default=32 * 1024)
    parser.add_argument('--num-cmds', type=int, default=32)
    args = parser.parse_args()

    # Set our global logging config here depending on what the user requested
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=level, format=log_format)
    logger = logging.getLogger('rw')

    # Create a NVMeDevice object for the slot we want to work with
    logger.info('Working on device {}'.format(args.pci_slot))
    nvme_device = NVMeDevice(args.pci_slot)

    # Disable, create queues, get namespace information
    nvme_device.cc_disable()
    nvme_device.init_admin_queues(asq_entries=16, acq_entries=16)
    nvme_device.cc_enable()
    nvme_device.identify()

    num_io_queues = 1
    io_queues_depth = 256
    logger.info('Creating {} IO queues with {} entries each'.format(num_io_queues, io_queues_depth))
    nvme_device.init_io_queues(num_io_queues, io_queues_depth)

    # Get the namespace's information
    ns = nvme_device.namespaces[args.namespace]

    # Make sure the namespace is valid
    assert ns is not None, 'NSID: {} is not valid on the drive'.format(args.namespace)

    # Namespace is valid, setup some params for the reads/writes
    ns_block_size = ns.lba_ds_bytes
    xfer_len = args.block_size
    num_blocks = xfer_len // ns_block_size
    nlb = num_blocks - 1

    # Create and map PRP for the write
    write_prp = PRP(xfer_len, nvme_device.mps)
    write_prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)

    # Create command, set PRP, fill in data
    write_cmd = Write(NSID=args.namespace, NLB=nlb)
    data_out = bytes([0xED] * xfer_len)
    write_prp.set_data_buffer(data_out)
    write_cmd.DPTR.PRP.PRP1 = write_prp.prp1
    write_cmd.DPTR.PRP.PRP2 = write_prp.prp2

    # Send the requested commands
    slba = args.slba
    for i in range(args.num_cmds):
        write_cmd.SLBA = slba
        write_cmd.complete = False
        nvme_device.sync_cmd(write_cmd, alloc_mem=False, timeout_s=1)
        slba += num_blocks

    # Create and map PRP for the read
    read_prp = PRP(xfer_len, nvme_device.mps)
    read_prp.alloc(nvme_device, DMADirection.DEVICE_TO_HOST)

    # Create command, set PRP
    read_cmd = Read(NSID=args.namespace, NLB=nlb)
    read_cmd.DPTR.PRP.PRP1 = read_prp.prp1
    read_cmd.DPTR.PRP.PRP2 = read_prp.prp2

    zero_data = bytes([0x00] * xfer_len)
    slba = args.slba
    for i in range(args.num_cmds):
        # Zero out the buffer so we can validate
        write_prp.set_data_buffer(zero_data)

        # Update SLBA
        read_cmd.SLBA = slba
        read_cmd.complete = False
        nvme_device.sync_cmd(read_cmd, alloc_mem=False, timeout_s=1)

        # Increment SLBA to the next one
        slba += num_blocks

        # Get the data in from the read prp
        data_in = read_prp.get_data_buffer()

        # Compare!
        assert data_out == data_in, 'Miscompare detected!'


if __name__ == '__main__':
    sys.exit(main())
