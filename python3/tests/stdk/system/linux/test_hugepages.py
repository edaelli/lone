import pytest

from stdk.system.linux.hugepages import HugePagesMemory


def test_hugepages():
    with HugePagesMemory() as mem_mgr:
        mem_mgr


def test_malloc(mocker):
    mocker.patch('hugepages.malloc', side_effect=[0x1000, 0x1000, 0])
    mem_mgr = HugePagesMemory()
    mem_1 = mem_mgr.malloc(4095)
    assert mem_1.vaddr == 0x1000
    mem_2 = mem_mgr.malloc(4096)
    assert mem_2.vaddr == 0x1000

    with pytest.raises(MemoryError):
        mem = mem_mgr.malloc(4096)
        assert mem == 0


def test_free(mocker):
    mocker.patch('hugepages.malloc', side_effect=[0x1000, 0x1000, 0x1000, 0x1000])
    mem_mgr = HugePagesMemory()
    mem_1 = mem_mgr.malloc(4095)
    assert mem_1.vaddr == 0x1000
    mem_2 = mem_mgr.malloc(4096)
    assert mem_2.vaddr == 0x1000

    mem_mgr.free(mem_1)
    mem_mgr.free([mem_2])

    with pytest.raises(MemoryError):
        mem_mgr.free([mem_2])

    mem_1 = mem_mgr.malloc(4095)
    assert mem_1.vaddr == 0x1000
    mem_2 = mem_mgr.malloc(4096)
    assert mem_2.vaddr == 0x1000
    mem_mgr.free_all()
