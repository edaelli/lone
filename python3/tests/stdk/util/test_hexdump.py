from stdk.util.hexdump import hexdump, hexdump_print


def test_hexdump(mocker):
    d = b'S\xe3' * 188

    # Test with sep
    mocker.patch('binascii.hexlify', side_effect=[b'testing'])
    hexdump(d)

    # Make it go down the no sep path
    mocker.patch('binascii.hexlify', side_effect=[TypeError])
    hexdump(d)

    mocker.patch('binascii.hexlify', side_effect=[b'testing'])
    hexdump_print(d)
