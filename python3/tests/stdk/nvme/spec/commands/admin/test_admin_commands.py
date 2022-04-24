

def test_importing_admin_commands():
    # Because commands are just classes, simply importing them is
    #  enough for testing. They end up getting tested individually
    #  as they are used in other tests
    from stdk.nvme.spec.commands.admin import identify
    assert identify

    from stdk.nvme.spec.commands.admin import create_io_completion_q
    assert create_io_completion_q

    from stdk.nvme.spec.commands.admin import create_io_submission_q
    assert create_io_submission_q
