import copy

import logging
logger = logging.getLogger('nvsim_pci')


class PCIeRegChangeHandler:

    def __init__(self, nvsim_state):
        self.nvsim_state = nvsim_state
        self.last_pcie_regs = copy.deepcopy(nvsim_state.pcie_regs)

    def __call__(self):
        # Make a copy right away to minimize things moving under us
        pcie_regs = copy.deepcopy(self.nvsim_state.pcie_regs)

        # NOTE: Dont use the comparable struct __eq__ here, it is slow.
        #   Use individual register changes as we need them
        #   No PCIe register changes supported yet

        # Save off the last time we checked
        self.last_pcie_regs = pcie_regs
