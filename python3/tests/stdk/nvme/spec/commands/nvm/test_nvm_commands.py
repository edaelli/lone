

def test_importing_nvm_commands():
    # Because commands are just classes, simply importing them is
    #  enough for testing. They end up getting tested individually
    #  as they are used in other tests
    from stdk.nvme.spec.commands.nvm import read
    assert read

    from stdk.nvme.spec.commands.nvm import write
    assert write
