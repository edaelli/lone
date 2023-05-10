import pytest

from lone.nvme.spec.commands.admin.get_log_page import GetLogPage
from lone.nvme.spec.commands.admin.get_log_page import GetLogPageSupportedLogPages


def test_get_invalid_log(nvme_device):
    # LID 0x17 is Reserved therefore should always result in an error
    glp_cmd = GetLogPage(LID=0x17)

    with pytest.raises(Exception):
        nvme_device.sync_cmd(glp_cmd, timeout_s=1)


def test_get_supported_logpages(nvme_device):
    glp_sup_lps = GetLogPageSupportedLogPages()

    nvme_device.sync_cmd(glp_sup_lps, timeout_s=1)
    assert glp_sup_lps.data_in.LIDS[0].LSUPP == 1
