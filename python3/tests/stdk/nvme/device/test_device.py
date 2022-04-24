

def test_device(mocked_system):

    # Test creating the object using the mocked system
    from stdk.nvme.device import NVMeDevice
    device = NVMeDevice('test_slot')

    # Test calling its interfaces
    device.map_dma_region_read(0, 0, 0)
    device.map_dma_region_write(0, 0, 0)
    device.map_dma_region_rw(0, 0, 0)
    device.unmap_dma_region(0, 0)
