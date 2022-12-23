import pytest
import ctypes
from types import SimpleNamespace

from lone.nvme.spec.queues import (NVMeHeadTail, NVMeQueue, NVMeSubmissionQueue,
                                   NVMeCompletionQueue, QueueMgr)
from lone.nvme.spec.structures import SQECommon, CQE
from lone.system import MemoryLocation


def test_nvme_queues_head_tail():
    q_mem = (ctypes.c_uint8 * 16 * 256)()
    q_address = ctypes.addressof(q_mem)

    ht = NVMeHeadTail(256, q_address)

    # Test setting
    ht.set(0)
    assert ht.value == 0

    # Test adding
    ht.add(1)
    ht.add(3)
    ht.add(1)
    assert ht.value == 5

    # Test add with wrapping
    ht.add(251)
    assert ht.value == 0
    ht.add(1)
    assert ht.value == 1

    # Test increment
    ht.set(0)
    assert ht.value == 0

    # Test incr doesnt change value
    assert ht.incr(1) == 1
    assert ht.value == 0

    # With wrapping
    assert ht.incr(256) == 0


def test_nvme_queues_nvme_queue():
    q_mem = (ctypes.c_uint8 * 16 * 256)()
    q_address = ctypes.addressof(q_mem)
    q_memory = MemoryLocation(q_address, q_address, ctypes.sizeof(q_mem), 'test_queues')

    dbh_mem = ctypes.c_uint32()
    dbh_address = ctypes.addressof(dbh_mem)

    dbt_mem = ctypes.c_uint32()
    dbt_address = ctypes.addressof(dbt_mem)

    q = NVMeQueue(q_memory, 256, 16, 0, dbh_address, dbt_address)

    # Check is_full
    assert q.is_full() is False
    assert q.num_entries() == 0

    # Make it full, check it
    q.head.add(1)
    assert q.num_entries() == 255

    # Test queue entries and head > tail
    q.tail.set(50)
    q.head.set(100)
    assert q.num_entries() == (256 - 100) + 50


def test_nvme_queues_sub_q():
    q_mem = (ctypes.c_uint8 * 16 * 256)()
    q_address = ctypes.addressof(q_mem)
    q_memory = MemoryLocation(q_address, q_address, ctypes.sizeof(q_mem), 'test_queues')

    dbt_mem = ctypes.c_uint32()
    dbt_address = ctypes.addressof(dbt_mem)

    q = NVMeSubmissionQueue(q_memory, 256, 16, 0, dbt_address)

    command = SQECommon()
    q.post_command(command)
    assert q.get_command() is not None
    assert q.get_command() is None


def test_nvme_queues_compl_q():
    q_mem = (ctypes.c_uint8 * 16 * 256)()
    q_address = ctypes.addressof(q_mem)
    q_memory = MemoryLocation(q_address, q_address, ctypes.sizeof(q_mem), 'test_queues')

    dbh_mem = ctypes.c_uint32()
    dbh_address = ctypes.addressof(dbh_mem)

    q = NVMeCompletionQueue(q_memory, 256, 16, 0, dbh_address)
    assert q.get_next_completion() is not None

    q.consume_completion()

    q.head.set(255)
    q.consume_completion()

    q.post_completion(CQE())


def test_nvme_queues_q_mgr():

    q_mgr = QueueMgr()
    q_mgr.add(SimpleNamespace(qid=0), SimpleNamespace(qid=0))
    q_mgr.add(SimpleNamespace(qid=1), SimpleNamespace(qid=1))
    assert len(q_mgr.all_cqids) == 2

    q_mgr.get(0, 0)
    q_mgr.get(1, 1)

    q_mgr.get(None, 1)

    with pytest.raises(KeyError):
        q_mgr.get(2, 2)

    assert q_mgr.get(1, None) is not None
    assert q_mgr.get(2, None) is None
    assert q_mgr.get(None, 1) is not None
    assert q_mgr.get(None, 2) is None

    # Add one more queue and then test next_iosq_id
    q_mgr.add(SimpleNamespace(qid=2), SimpleNamespace(qid=2))
    q_mgr.next_iosq_id()
    q_mgr.next_iosq_id()
    q_mgr.next_iosq_id()
