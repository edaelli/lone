''' Python interface to manage hugepages memory
'''
import os
import hugepages

from stdk.system import Memory, MemoryLocation

import logging
logger = logging.getLogger('hugepages')


class HugePagesMemory(Memory):

    def __init__(self):
        hugepages.init()

        # Initialize parent
        super().__init__()

        # Save off size
        self.hugepages_size = hugepages.get_size()

    def malloc(self, size, align=os.sysconf('SC_PAGE_SIZE')):

        # Only allow SC_PAGE_SIZE sized allocations
        if size % self.SC_PAGE_SIZE:
            size = self.SC_PAGE_SIZE * (round(size / self.SC_PAGE_SIZE) + 1)

        # Call our C extension to allocate memory
        vaddr = hugepages.malloc(size, align)
        if vaddr == 0 or vaddr == -1:
            raise MemoryError('Not able to allocate {} {}'.format(size, align))

        # Create a MemoryLocation object and save it off in our
        #   tracking list
        mem_location = MemoryLocation(vaddr, size, align)
        self.allocated_mem_addrs.append(mem_location)

        logger.debug('malloc: v: 0x{:x} s: {}'.format(mem_location.vaddr, mem_location.size))

        return mem_location

    def free(self, memory):

        if type(memory) == list:
            mem_list = memory
        else:
            mem_list = [memory]

        for memory in mem_list:
            # Free only memory that are in out list
            if memory in self.allocated_mem_addrs:
                # Call our C extension to free memory and remove
                #   it from our tracking list
                hugepages.free(memory.vaddr)
                self.allocated_mem_addrs.remove(memory)

                logger.debug('freed: v: 0x{:x} s: {}'.format(memory.vaddr, memory.size))
            else:
                # Raise if the user requested us to free memory we don't own
                raise MemoryError('Invalid free memory: 0x{:x}'.format(memory.vaddr))

    def free_all(self):
        ''' Free all memory we previously allocated
        '''
        while self.allocated_mem_addrs:
            mem_location = self.allocated_mem_addrs.pop(0)

            # Call our C extension to free memory and remove it
            #   from our list
            hugepages.free(mem_location.vaddr, mem_location.size)

            logger.debug('freed: v: 0x{:x} s: {}'.format(mem_location.vaddr, mem_location.size))

    def __enter__(self):
        ''' Enter the context manager
        '''
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        ''' Exit the context manager cleaning up all our memory
        '''
        # Free all memory
        self.free_all()
        hugepages.finish()
