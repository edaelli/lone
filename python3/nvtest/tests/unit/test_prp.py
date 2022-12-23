import pytest
import ctypes

from lone.system import DMADirection
from lone.nvme.spec.prp import PRP


def test_prp(nvme_device):
    prp = PRP(4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)

    prp = PRP(2 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)

    prp = PRP(20 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)

    # Set prps_per_page to 1 to go down assert path
    prp = PRP(20 * 4096, 4096)
    prp.prps_per_page = 1
    with pytest.raises(AssertionError):
        prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)


def test_prp_from_address():
    prp1_mem = (ctypes.c_uint8 * 4096)()
    prp1_address = ctypes.addressof(prp1_mem)

    prp2_mem = (ctypes.c_uint8 * 4096)()
    prp2_address = ctypes.addressof(prp2_mem)
    prp2_mem[0] = 0xFF

    prp = PRP(4096, 4096)
    prp.from_address(prp1_address, prp2_address)

    prp = PRP(2 * 4096, 4096)
    prp.from_address(prp1_address, prp2_address)

    prp = PRP(20 * 4096, 4096)
    prp.from_address(prp1_address, prp2_address)


def test_prp_str(nvme_device):
    prp = PRP(4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    s = prp.__str__()
    assert s != ''

    prp = PRP(2 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    s = prp.__str__()
    assert s != ''

    prp = PRP(20 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    s = prp.__str__()
    assert s != ''

    prp = PRP(20 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    prp.mem_list = []
    s = prp.__str__()
    assert s == ''

    prp = PRP(20 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    prp.mps = 0
    s = prp.__str__()
    assert s != ''


def test_get_data_segments(nvme_device):
    prp = PRP(4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    prp.get_data_segments()

    prp = PRP(2 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    prp.get_data_segments()

    prp = PRP(4 * 4096, 4096)
    prp.alloc(nvme_device, DMADirection.HOST_TO_DEVICE)
    prp.get_data_segments()
