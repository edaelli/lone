from stdk.system import System


class NVMeDevice:

    def __init__(self, pci_slot):
        # Save off our slot
        self.pci_slot = pci_slot

        # Create the PCI Userspace device interface object
        self.pci_userspace_dev_ifc = System.PciUserspaceDevice(pci_slot)

        # Create the object to access PCIe registers, and init cababilities
        self.pcie_regs = self.pci_userspace_dev_ifc.pci_regs()
        self.pcie_regs.init_capabilities()

        # Create the object to access NVMe registers
        self.nvme_regs = self.pci_userspace_dev_ifc.nvme_regs()

    def map_dma_region_read(self, vaddr, iova, size):
        self.pci_userspace_dev_ifc.map_dma_region_read(vaddr, iova, size)

    def map_dma_region_write(self, vaddr, iova, size):
        self.pci_userspace_dev_ifc.map_dma_region_write(vaddr, iova, size)

    def map_dma_region_rw(self, vaddr, iova, size):
        self.pci_userspace_dev_ifc.map_dma_region_rw(vaddr, iova, size)

    def unmap_dma_region(self, iova, size):
        self.pci_userspace_dev_ifc.unmap_dma_region(iova, size)
