''' OS Independent interfaces
'''
import os
import platform
import abc


class SysRequirements(metaclass=abc.ABCMeta):
    ''' Checks that the running hardware meets stdk requirements
    '''
    @abc.abstractmethod
    def check_requirements(self):
        raise NotImplementedError


class SysPci(metaclass=abc.ABCMeta):
    ''' Interface to access the PCI subsystem within an Operating System
    '''
    @abc.abstractmethod
    def rescan(self):
        ''' Rescans the PCI bus
        '''
        raise NotImplementedError


class SysPciDevice(metaclass=abc.ABCMeta):
    ''' Interface to access one PCI device within an Operating System
    '''
    def __init__(self, pci_slot):
        self.pci_slot = pci_slot

    @abc.abstractmethod
    def exists(self):
        ''' Returns true if this device exists in the OS, false otherwise
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self):
        ''' Remove the device from the OS
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def expose(self, user):
        ''' Exposes the device to a user in userspace
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def reclaim(self, driver):
        ''' Reclaims the device from a user in userspace and
            tries to bind it to the requested driver
        '''
        raise NotImplementedError


class SysPciUserspace(metaclass=abc.ABCMeta):
    ''' Interface to interact to an Operating System's PCI userspace access
        Implemented with VFIO in Linux
    '''
    @abc.abstractmethod
    def devices(self):
        ''' List available devices
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def exposed_devices(self):
        ''' List available devices that have been exposed to a user in userspace
        '''
        raise NotImplementedError


class SysPciUserspaceDevice(metaclass=abc.ABCMeta):
    ''' Interface to access a Pci device from userspace, generally through
        the system's IOMMU for secure access
        Implemented with VFIO in Linux
    '''
    def __init__(self, pci_slot, pci_vid=None, pci_did=None,
                 driver=None, owner=None, info_string=None):
        self.pci_slot = pci_slot
        self.pci_vid = pci_vid
        self.pci_did = pci_did
        self.driver = driver
        self.owner = owner
        self.info_string = info_string

    @abc.abstractmethod
    def pci_regs(self):
        ''' Returns an object with the pci registers for the device
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def nvme_regs(self):
        ''' Returns an object with the nvme registers for the device
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def map_dma_region_read(self, vaddr, iova, size):
        ''' Map a DMA region for READ ONLY
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def map_dma_region_write(self, vaddr, iova, size):
        ''' Map a DMA region for WRITE ONLY
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def map_dma_region_rw(self, vaddr, iova, size):
        ''' Map a DMA region for WRITE ONLY
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def unmap_dma_region(self, iova, size):
        ''' Unmap DMA region
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self):
        ''' Reset the device
        '''
        raise NotImplementedError


class MemoryLocation:
    ''' Generic memory location object
    '''
    def __init__(self, vaddr, size, align):
        self.vaddr = vaddr
        self.size = size
        self.align = align
        self.iova = None
        self.flags = None


class Memory(metaclass=abc.ABCMeta):
    ''' Base memory interface object
    '''
    SC_PAGE_SIZE = os.sysconf('SC_PAGE_SIZE')

    def __init__(self):
        ''' Initializes a memory manager
        '''
        self.allocated_mem_addrs = []

    @abc.abstractmethod
    def malloc(self, size, align=os.sysconf('SC_PAGE_SIZE')):
        ''' Allocates memory
        '''
        raise NotImplementedError

    def __enter__(self):
        ''' Enter the context manager
        '''
        return self

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        ''' Exit the context manager cleaning up all our memory
        '''
        pass

    @abc.abstractmethod
    def free(self, memory):
        ''' Free previously allocated memory
        '''
        raise NotImplementedError

    def get(self, vaddr):
        ''' Get a previously allocated memory location by virtual address
        '''
        for memory in self.allocated_mem_addrs:
            if memory.vaddr == vaddr:
                return memory
        return None

    def free_all(self):
        ''' Free all memory we previously allocated
        '''
        while self.allocated_mem_addrs:
            mem_location = self.allocated_mem_addrs.pop(0)

            # Free it
            self.free(mem_location.vaddr)


# Now for each supported OS, pick the objects that implement the
#  interfaces above
if platform.system() == 'Linux':
    from stdk.system.linux import pci, vfio, requirements
    requirements = requirements.LinuxRequirements
    syspci = pci.LinuxSysPci
    syspci_device = pci.LinuxSysPciDevice
    syspci_userspace = vfio.SysVfio
    syspci_userspace_device = vfio.SysVfioIfc

    # If the user is calling this before installing stdk
    #   hugepages will not be there. We don't want to fail
    #   here so just leave the MemoryMgr empty
    try:
        from stdk.system.linux import hugepages
        mem_mgr = hugepages.HugePagesMemory
        mem_mgr()
    except ModuleNotFoundError:
        print('WARNING: Running without a MemoryMgr')
        mem_mgr = None
else:
    raise NotImplementedError


class System:
    Requirements = requirements
    Pci = syspci
    PciDevice = syspci_device
    PciUserspace = syspci_userspace
    PciUserspaceDevice = syspci_userspace_device
    MemoryMgr = mem_mgr
