from stdk.nvme.spec.registers.nvme_regs import NVMeRegisters


def test_nvme_regs():
    regs = NVMeRegisters()
    regs.log()
