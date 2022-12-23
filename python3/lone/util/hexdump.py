import io
import binascii

import logging
logger = logging.getLogger('hexdump')


def hexlify_with_string(chunk):
    # Make a space separated string of hex bytes
    try:
        h = binascii.hexlify(chunk, sep=' ').decode()
    except TypeError:
        h = binascii.hexlify(chunk).decode()

    # Make the equivalent ascii string with . for unprintable
    s = ''
    for i in chunk:
        if i > 31 and i < 128:
            s += chr(i)
        else:
            s += '.'
    return h, s


def hexdump(data, num_chunks=16, max_bytes=None):
    # Make a bytes io object, and iterate reading
    #  it in num_chunks chunks. Then hexlify the
    #  results into a list of hex lines.
    bio = io.BytesIO(data)
    chunks = iter(lambda: bio.read(num_chunks), b'')
    hexlines = map(hexlify_with_string, chunks)

    if max_bytes:
        max_lines = max_bytes // num_chunks
    else:
        max_lines = None
    ret = []

    # Make sure all strings are the same length,
    #  pad with spaces.
    length = (num_chunks * 2) + (num_chunks - 1)

    # Create the string
    address = 0
    for h, s in hexlines:
        h = h.ljust(length)
        ret.append('0x{:04x} {}   {}'.format(address, h, s))
        address += num_chunks

        if max_lines:
            if len(ret) >= max_lines:
                break

    # Return it
    return ret


def hexdump_print(data, printer=logger.debug, num_chunks=16):
    for line in hexdump(data, num_chunks):
        printer(line)
