import pytest
from types import SimpleNamespace


from lone.system.linux.hugepages_mgr import HugePagesMemoryMgr


def test_hugepages_memory_mgr(mocker):
    mocker.patch('hugepages.init', return_value=None)
    mocker.patch('hugepages.malloc', side_effect=range(0x1000, 0x10000000, 2 * 1024 * 1024))
    mocker.patch('hugepages.get_size', return_value=2 * 1024 * 1024)
    mocker.patch('hugepages.free', return_value=None)
    mocker.patch('ctypes.memset', return_value=None)

    hp_mem_mgr = HugePagesMemoryMgr(4096)

    assert len(hp_mem_mgr.free_pages()) != 0
    assert hp_mem_mgr.allocated_mem_list() is not None

    # Test malloc
    mem = hp_mem_mgr.malloc(1)
    assert mem.size == 4096

    mem = hp_mem_mgr.malloc(4096)
    assert mem.size == 4096

    mem = hp_mem_mgr.malloc(10 * 4096)
    assert mem.size == 40960

    mem = hp_mem_mgr.malloc(1000 * 4096)
    assert mem.size == 4096000

    def test(num):
        return None
    hp_mem_mgr._malloc_hps = test
    free_pages = []
    for page in range(10):
        free_pages.append(SimpleNamespace(vaddr=1000, size=4096, in_use=True))
    for page in range(10):
        free_pages.append(SimpleNamespace(vaddr=1000, size=4096, in_use=False))
    hp_mem_mgr.free_pages = lambda: free_pages
    with pytest.raises(MemoryError):
        mem = hp_mem_mgr.malloc(10 * 4096)

    # Test malloc_pages
    free_pages = []
    for page in range(10):
        free_pages.append(SimpleNamespace(vaddr=1000, size=4096, in_use=True))
    hp_mem_mgr.free_pages = lambda: free_pages
    hp_mem_mgr.malloc_pages(1)
    with pytest.raises(AssertionError):
        hp_mem_mgr.malloc_pages(11)
    hp_mem_mgr.free(mem)
    hp_mem_mgr.free_all()

    # Test free
    hp_mem_mgr = HugePagesMemoryMgr(4096)
    mem = hp_mem_mgr.malloc(1)
    hp_mem_mgr.free(mem)
    mem = hp_mem_mgr.malloc(40960)
    hp_mem_mgr.free(mem)

    # Test free_all
    hp_mem_mgr.free_all()

    # Test __enter__, __exit__
    with HugePagesMemoryMgr(4096) as mem_mgr:
        mem_mgr


def test_hugepages_memory(mocker):
    mocker.patch('hugepages.init', return_value=None)
    mocker.patch('hugepages.malloc', return_value=0)
    mocker.patch('hugepages.get_size', return_value=2 * 1024 * 1024)
    mocker.patch('hugepages.free', return_value=None)

    with pytest.raises(MemoryError):
        HugePagesMemoryMgr(4096)
