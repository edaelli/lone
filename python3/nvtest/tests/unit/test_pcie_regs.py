import pytest
import ctypes
import tempfile

from lone.nvme.spec.registers.pcie_regs import (
    PCIeRegistersDirect,
    PCIeRegistersIndirect,
    PCICapPowerManagementInterface
)


def check_registers(pcie_regs):

    ################################################################################
    #  Check fields that are substructures
    ################################################################################

    # Values are initialized to 0
    assert pcie_regs.ID.VID == 0
    assert pcie_regs.ID.DID == 0

    # Test assigning with a new structure with init values
    pcie_regs.ID = type(pcie_regs.ID)(VID=0x1234, DID=0x5678)
    assert pcie_regs.ID.VID == 0x1234
    assert pcie_regs.ID.DID == 0x5678

    # Update individual values and check
    pcie_regs.ID.VID = 0x1234
    assert pcie_regs.ID.VID == 0x1234
    assert pcie_regs.ID.DID == 0x5678

    pcie_regs.BAR2 = 0xFFFFFFFF
    assert pcie_regs.BAR2 == 0xFFFFFFFF

    # Invalid attribute
    with pytest.raises(AttributeError):
        pcie_regs.INVALID

    ################################################################################
    #  Check fields that are just ctypes (not structures)
    ################################################################################

    # Make sure it inits to 0
    assert pcie_regs.RID == 0

    # Update and test
    pcie_regs.RID = 0x12
    assert pcie_regs.RID == 0x12

    ################################################################################
    #  Check fields that are ctype arrays
    ################################################################################

    # Make sure it inits to 0
    for i in pcie_regs.RSVD_0:
        assert i == 0

    # Fill it with 0, 1, 2...
    pcie_regs.RSVD_0 = (ctypes.c_ubyte * 5)(*([i for i in range(5)]))

    # Check it
    for i, v in enumerate(pcie_regs.RSVD_0):
        assert i == v

    # Test capabilities on each type of registers. Only minimal testing, more
    #  complete testing in another function
    pcie_regs.CAP.CP = 0x40
    pcie_regs.RSVD_CAP[0] = 0
    pcie_regs.init_capabilities()


def test_reg_access_direct():
    direct = PCIeRegistersDirect()
    assert ctypes.sizeof(direct) == 4096
    check_registers(direct)


def test_reg_access_indirect():
    # Create a fake pcie registers file for indirect testing
    tf = tempfile.NamedTemporaryFile()
    file_size = 8192

    with open(tf.name, 'wb+') as fh:
        fh.write(bytearray(file_size))
        fh.flush()
        indirect = PCIeRegistersIndirect(fh.fileno(), 0, 8192)
        check_registers(indirect)

        # Check a field that is not supported (uint16), but should not exist in the
        #  spec anyway
        with pytest.raises(AttributeError):
            indirect.RSVD_1


def test_log():
    pcie_regs = PCIeRegistersDirect()
    pcie_regs.log()


def test_cap():
    pcie_regs = PCIeRegistersDirect()

    # Create a PCICapPowerManagementInterface capability and test it out
    pcie_regs.CAP.CP = 0x40
    cap = PCICapPowerManagementInterface.from_address(ctypes.addressof(pcie_regs.RSVD_CAP))
    cap.CAP_ID = PCICapPowerManagementInterface.cap_id
    cap.NEXT_PTR = 0x00
    cap.PC = PCICapPowerManagementInterface.Pc(0x00)
    cap.PMCS = PCICapPowerManagementInterface.Pmcs(0x00)
    cap.pointer = 0x40
    cap.log()
