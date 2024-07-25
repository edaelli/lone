''' OS Independent interfaces
'''
import os
import sys
import platform
import abc
import importlib.util
from enum import Enum


class SysRequirements(metaclass=abc.ABCMeta):
    ''' Checks that the running hardware meets lone requirements
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


class DMADirection(Enum):
    ''' DMA directions for memory transfer and mapping
    '''
    HOST_TO_DEVICE = 1
    DEVICE_TO_HOST = 2
    BIDIRECTIONAL = 3


class IovaMgr:
    ''' This class manages how IOVAs are assigned to memory
        NOTE: Limits it to 2M requests
    '''
    def __init__(self, iova_base):
        self.iova_base = iova_base
        next_available_iova = self.iova_base

        self.free_iovas = []
        for i in range(100):
            self.free_iovas.append(next_available_iova)
            next_available_iova += (2 * 1024 * 1024)

    def get(self, size):
        assert size < (2 * 1024 * 1024)
        ret = self.free_iovas.pop(0)
        return ret

    def free(self, iova):
        self.free_iovas.append(iova)


class MemoryLocation:
    ''' Generic memory location object
    '''
    def __init__(self, vaddr, iova, size, client, in_use=True):
        self.vaddr = vaddr
        self.size = size
        self.iova = iova
        self.client = client
        self.in_use = in_use

        # List of addresses that are linked (wrt being allocated or not to this memory)
        self.linked_mem = []


class Memory(metaclass=abc.ABCMeta):
    ''' Base memory interface object
    '''
    def __init__(self, page_size):
        ''' Initializes a memory manager
        '''
        self.page_size = page_size
        self.iova_mgr = IovaMgr(0xED000000)

    @abc.abstractmethod
    def malloc(self, size, client=None):
        ''' Allocates low level system memory that can be split up by malloc below
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def malloc_pages(self, num_pages, client=None):
        ''' Allocates a list of MemoryLocation objects of Memory.page_size sized
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def __enter__(self):
        ''' Enter the context manager
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        ''' Exit the context manager cleaning up all our memory
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def free(self, memory):
        ''' Frees previoulsy allocated memory
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def free_all(self):
        ''' Free all memory we previously allocated
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def allocated_mem_list(self):
        ''' Returns a list of all allocated memory
        '''
        raise NotImplementedError


# Now for each supported OS, pick the objects that implement the
#  interfaces above
if platform.system() == 'Linux':
    from lone.system.linux import pci, vfio, requirements
    requirements = requirements.LinuxRequirements
    syspci = pci.LinuxSysPci
    syspci_device = pci.LinuxSysPciDevice
    syspci_userspace = vfio.SysVfio
    syspci_userspace_device = vfio.SysVfioIfc

    # If the user is calling this before installing lone
    #   hugepages will not be there. We don't want to fail
    #   here so just leave the MemoryMgr empty
    # Using importlib to be able to test it in unittests
    mem_mgr = None
    hp_spec = importlib.util.find_spec('lone.system.linux.hugepages_mgr')
    if hp_spec is not None:
        try:
            hp_module = importlib.util.module_from_spec(hp_spec)
            sys.modules['hugepages_mgr'] = hp_module
            hp_spec.loader.exec_module(hp_module)
            mem_mgr = hp_module.HugePagesMemoryMgr
        except ModuleNotFoundError:
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
