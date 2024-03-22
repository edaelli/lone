from lone.util.lba_gen import LBARandGenLFSR


def test_lba_gen():
    max_lba = 0x10000
    bs = 5
    initial_state = 23
    start_lba = 11
    lbas = LBARandGenLFSR(max_lba, bs, initial_state=initial_state, start_lba=start_lba)

    lba_list = []

    # Check that all lbas are valid
    for lba in lbas:
        lba_list.append(lba)
        assert lba <= (max_lba - bs)
        assert lba >= start_lba

    # Check that all LBAs are unique
    assert len(set(lba_list)) == ((max_lba - start_lba) // bs)

    # Check that all LBAs are there
    s = list(sorted(lba_list))

    # Check that all LBAs match
    for i in range(len(s)):
        assert (i * bs) + start_lba == s[i]

    lbas.reset()
    assert lbas.initial_state == initial_state
    assert lbas.period == 0
    assert lbas.complete is False
