import ctypes
from lone.util import logging
from lone.util.hexdump import hexdump, hexdump_print
from lone.util.struct_tools import ComparableStruct, StructFieldsIterator


def test_hexdump(mocker):
    d = b'S\xe3' * 188

    # Test with sep
    mocker.patch('binascii.hexlify', side_effect=[b'testing'])
    hexdump(d)
    mocker.patch('binascii.hexlify', side_effect=[b'testing'])
    hexdump(d, max_bytes=16)
    mocker.patch('binascii.hexlify', side_effect=[b'testing'])
    hexdump(d, max_bytes=32)

    # Make it go down the no sep path
    mocker.patch('binascii.hexlify', side_effect=[TypeError])
    hexdump(d)

    mocker.patch('binascii.hexlify', side_effect=[b'testing'])
    hexdump_print(d)


# Structure for all tests to use
class STest(ComparableStruct):
    _fields_ = [
        ('TEST', ctypes.c_uint32),
        ('TEST_ARRAY', ctypes.c_uint32 * 2)
    ]


def test_comp_struct():

    # Test that structures with identical fields are
    #  considered to be equal
    s1 = STest()
    s2 = STest()
    assert s1 == s2
    assert not s1 != s2

    # Test that structures with different fields are
    #  considered not equal
    s1 = STest()
    s2 = STest()
    s2.TEST = 0xFF
    assert not s1 == s2
    assert s1 != s2

    # Test the code that checks for arrays for equality/inequality
    s1 = STest()
    s2 = STest()
    s2.TEST_ARRAY[0] = 0xFF
    assert not s1 == s2
    assert s1 != s2


def test_struct_field_iterator():

    # Test the structure iterator
    it = StructFieldsIterator(STest())

    # Make sure it emits the correct values
    f, v = next(it)
    assert f == 'STest.TEST' and v == 0

    f, v = next(it)
    assert f == 'STest.TEST_ARRAY[0]' and v == 0

    f, v = next(it)
    assert f == 'STest.TEST_ARRAY[1]' and v == 0

    # Make sure the iterator runs and finishes
    for f, v in StructFieldsIterator(STest()):
        pass


def test_logging():
    logging
