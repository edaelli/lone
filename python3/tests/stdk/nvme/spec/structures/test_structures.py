import pytest
from stdk.nvme.spec.structures import SQECommon, DataOutCommon, DataInCommon, CQE


def test_sqe_common():
    sqe = SQECommon()
    assert sqe.OPC == 0x00
    assert sqe.DW2 == 0x00
    assert len(sqe) == 40

    with pytest.raises(AttributeError):
        sqe.NOT_VALID = 1

    class SQEWithDefaults(SQECommon):
        _defaults_ = {
            'OPC': 0x01,
            'DW2': 0x02,
        }
    sqe = SQEWithDefaults()
    assert sqe.OPC == 0x01
    assert sqe.DW2 == 0x02


def test_data_common():
    d_in = DataInCommon()
    assert len(d_in) == 0

    d_out = DataOutCommon()
    assert len(d_out) == 0


def test_cqe():
    cqe = CQE()
    assert cqe.P == 0
    with pytest.raises(AttributeError):
        assert cqe.A is None
    assert len(cqe) == 16

    cqe.P = 1
    assert cqe.P == 1

    cqe.CID = 1
    assert cqe.CID == 1
