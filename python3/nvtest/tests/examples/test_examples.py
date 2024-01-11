''' Test module for examples on how to use lone
'''
import pytest


def test_example_config(lone_config):
    # The lone_config fixture is the dictionary representation
    #   of the yaml file passed into pytest with the --config
    #   option.
    #   For example:
    #   pytest --config /tmp/example.yml
    #   example.yml contains
    #   dut:
    #      pci_slot: nvsim
    #   Then lone_config will look like:
    #   lone_config = {'dut': {'pci_slot': 'nvsim'}}
    #   See configuration documentation for all options
    assert 'dut' in lone_config.keys()
    assert 'pci_slot' in lone_config['dut'].keys()


def test_nvme_device_raw(nvme_device_raw):
    # The nvme_device_raw fixture is the bare nvme device
    #  which can be accessed by PCIe and NVMe registers, and
    #  has not had anything done to it. For example, it is in
    #  an unknown (likely disabled) state, and no queues have
    #  been created, etc. This allows for testing of very low
    #  level operations like creating queues, etc.
    #  The nvme_device_raw is configured by the information
    #  in the lone config file passed in as the --config parameter

    # Check the registers are of the right type
    from lone.nvme.spec.registers.pcie_regs import PCIeRegisters
    assert issubclass(type(nvme_device_raw.pcie_regs), PCIeRegisters)

    from lone.nvme.spec.registers.nvme_regs import NVMeRegistersDirect
    assert type(nvme_device_raw.nvme_regs) is NVMeRegistersDirect

    # Check a couple of values in pcie and nvme for demonstration

    # Make sure that PCIe VID and DID are not zero
    assert nvme_device_raw.pcie_regs.ID.VID != 0
    assert nvme_device_raw.pcie_regs.ID.DID != 0

    # Make sure that NVMe VS is not zero
    assert nvme_device_raw.nvme_regs.VS.MJR != 0
    assert nvme_device_raw.nvme_regs.VS.MNR != 0
    assert type(nvme_device_raw.nvme_regs.VS.__str__) is str

    # Disable the device, setup admin queues, re-enable it
    nvme_device_raw.cc_disable()
    nvme_device_raw.init_admin_queues(asq_entries=64, acq_entries=256)
    nvme_device_raw.cc_enable()

    # Make sure it is ready after enable
    assert nvme_device_raw.nvme_regs.CSTS.RDY == 1

    # At this point the device is ready to take in ADMIN commands
    # Let's try an Identify (CNS=1 Controller)

    # First create the command object
    from lone.nvme.spec.commands.admin.identify import IdentifyController
    id_ctrl_cmd = IdentifyController()

    # Then send it to the device, and wait for a completion
    nvme_device_raw.sync_cmd(id_ctrl_cmd)

    # Getting here means that sync_cmd sent the command to the device on the
    #  admin submission queue, then found a completion in the admin completion
    #  queue for it. sync_cmd can (and does by default) check status on the
    #  completion, but let's do it here to demonstrate
    # If the command failed, cqe.SF.SC would be non-zero
    assert id_ctrl_cmd.cqe.SF.SC == 0x0, 'Identify command failed with SC=0x{:02x}'.format(
                                         id_ctrl_cmd.cqe.SF.SC)

    # Ok, the identify controller command was sucessful, this means we can look at the
    #   returned data
    assert id_ctrl_cmd.data_in.MN != '', 'Empty Model Number'
    assert id_ctrl_cmd.data_in.SN != '', 'Empty Serial Number'
    assert id_ctrl_cmd.data_in.FR != '', 'Empty Firmware Revision'


@pytest.mark.parametrize(
    'nvme_device',
    [{'asq_entries': 10, 'acq_entries': 20, 'num_io_queues': 10, 'io_queue_entries': 10}],
    indirect=True)
def test_nvme_device(nvme_device, lone_config):
    # The nvme_device fixture is similar to the nvme_device_raw
    #  fixture, except it has initialized admin and io queues on
    #  the device before the test starts.
    #  You can set parameters to how many queues, slots, etc by
    #  decorating this function as shown above.

    # Check that the inittialization matches the setup above
    assert nvme_device.nvme_regs.AQA.ASQS == (10 - 1)  # Zero based
    assert nvme_device.nvme_regs.AQA.ACQS == (20 - 1)  # Zero based
    assert len(nvme_device.queue_mgr.nvme_queues) == 1 + 10  # Admin + NVM queues

    # Check that the device is enabled
    assert nvme_device.nvme_regs.CSTS.RDY == 1

    # Ok, now we can demonstrate how to send a NVM command (Read in this case)
    #  The first step of sending a read is to allocate memory and build a PRP
    #  for it
    from lone.nvme.spec.commands.nvm.read import Read
    from lone.nvme.spec.prp import PRP
    from lone.system import DMADirection

    # We are going to try a 4096 byte read to LBA 0 to demonstrate
    xfer_len = 4096
    slba = 0

    # Calculating the NLB for 4096 bytes of data depends on the namespace's
    #  data size which has been saved when we call the
    #  nvme_device.identify_namespaces interface
    nvme_device.identify_namespaces()
    nsid = lone_config['dut']['namespaces'][0]['nsid']
    ns = nvme_device.namespaces[nsid]
    ns_block_size = ns.lba_ds_bytes
    num_blocks = xfer_len // ns_block_size
    nlb = num_blocks - 1

    # Allocating memory and creating a PRP is easy, but a 2 step process. First we
    #  create the PRP object, then allocate device memory to associate with it
    #  Since this is a read, we tell the IOMMU to only allow transfers to this
    #  memory from the device to host direction.
    read_prp = PRP(xfer_len, nvme_device.mps)
    read_prp.alloc(nvme_device, DMADirection.DEVICE_TO_HOST)

    # Create the command, setup parameters, and add PRP
    read_cmd = Read(SLBA=slba, NLB=nlb, NSID=nsid)
    read_cmd.DPTR.PRP.PRP1 = read_prp.prp1
    read_cmd.DPTR.PRP.PRP2 = read_prp.prp2

    # Send the command, wait for completion, check status
    nvme_device.sync_cmd(read_cmd)

    # At this point the command completed, we can look at the read data
    read_data = read_prp.get_data_buffer()

    # Check that we got as much data as we asked for
    assert len(read_data) == xfer_len

    # Disable the device at the end of the test
    nvme_device.cc_disable()
    assert nvme_device.nvme_regs.CSTS.RDY == 0
