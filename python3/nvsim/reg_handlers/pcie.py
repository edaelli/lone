import logging
logger = logging.getLogger('nvsim_pci')


class PCIeRegChangeHandler:

    def __init__(self, nvsim_state):
        self.nvsim_state = nvsim_state
        self.pcie_regs_data = bytearray(self.nvsim_state.pcie_regs)

    def __call__(self):
        # Make a copy right away to minimize things moving under us
        pcie_regs_data_old = self.pcie_regs_data
        pcie_regs_data_new = bytearray(self.nvsim_state.pcie_regs)

        # If old != new go check if we need to do anything
        if pcie_regs_data_old != pcie_regs_data_new:
            for i in range(len(pcie_regs_data_new)):
                if pcie_regs_data_old[i] != pcie_regs_data_new[i]:
                    logging.info('PCIE changed at offset 0x{:x}'.format(i))

        # Save off the last time we checked
        self.pcie_regs_data = pcie_regs_data_new
