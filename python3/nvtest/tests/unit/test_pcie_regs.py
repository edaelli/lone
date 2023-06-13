import pytest
import ctypes

from lone.nvme.spec.registers.pcie_regs import (PCIeRegistersDirect,
                                                PCICapPowerManagementInterface,
                                                pcie_reg_struct_factory,
                                                PCIeRegisters,
                                                PCIeAccessData)


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

    # TODO: Re-enable
    # pcie_regs.BAR2 = 0xFFFFFFFF
    # assert pcie_regs.BAR2 == 0xFFFFFFFF

    # Invalid attribute
    with pytest.raises(AttributeError):
        pcie_regs.INVALID

    ################################################################################
    #  Check fields that are just ctypes (not structures)
    ################################################################################

    # Make sure it inits to 0
    # assert pcie_regs.Rid.RID == 0

    # Update and test
    # pcie_regs.RID = 0x12
    # assert pcie_regs.RID == 0x12

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


def test_indirect_access(mocker):

    test_data = [0] * 4096

    def read_byte(offset):
        return test_data[offset]

    def write_byte(offset, value):
        test_data[offset] = value

    class Registers(pcie_reg_struct_factory(PCIeAccessData(read_byte, write_byte)), PCIeRegisters):
        pass
    pcie_regs = Registers()

    # Make sure there is a _fields_ attribute
    assert pcie_regs._fields_ is not None

    # Test that getting an attribute results in the right type
    assert type(pcie_regs.ID) == Registers.Id

    # Tests that setting default values works
    test_data = [0] * 4096
    pcie_regs.ID = Registers.Id(VID=0xFFFF)
    pcie_regs.ID.DID = 0xED11
    assert pcie_regs.ID.VID == 0xFFFF
    assert pcie_regs.ID.DID == 0xED11
    assert test_data[0] == 0xFF
    assert test_data[1] == 0xFF
    assert test_data[2] == 0x11
    assert test_data[3] == 0xED

    # Set a new attribute to check that path
    pcie_regs.ID.test = 0
