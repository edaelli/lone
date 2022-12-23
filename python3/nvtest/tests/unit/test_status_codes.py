import pytest

from lone.nvme.spec.structures import ADMINCommand
from lone.nvme.spec.commands.status_codes import (status_codes,
                                                  NVMeStatusCode,
                                                  NVMeStatusCodeException)


def test_status_codes():
    code = NVMeStatusCode(0x00, 'Test', ADMINCommand)
    assert code.failure is False
    assert code.success is True

    # Add our code so we can test it
    status_codes.add(code)

    # Test SCT = 0 path
    cmd = ADMINCommand()
    cmd.cqe.SF.SCT = 0
    status_codes.get(cmd)

    # Test SCT != 0 path
    cmd = ADMINCommand()
    cmd.cqe.SF.SCT = 1
    status_codes.get(cmd)

    # Test check interface
    cmd = ADMINCommand()
    cmd.cqe.SF.SCT = 0
    status_codes.check(cmd)

    cmd = ADMINCommand()
    cmd.cqe.SF.SCT = 1
    with pytest.raises(NVMeStatusCodeException):
        status_codes.check(cmd)

    cmd = ADMINCommand()
    cmd.cqe.SF.SCT = 1
    status_codes.check(cmd, raise_exc=False)


def test_status_code_get_item():
    # Test getitem
    assert status_codes[0].value == 0
    assert status_codes[0].name == 'Successful Completion'

    assert status_codes['Successful Completion'].value == 0
    assert status_codes['Successful Completion'].name == 'Successful Completion'

    assert status_codes['INVALID'] is None

    with pytest.raises(AssertionError):
        status_codes[0.01]
