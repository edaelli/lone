# https://datacipy.cz/lfsr_table.pdf
# https://blog.xojo.com/2021/10/01/random-numbers-with-lfsr-linear-feedback-shift-register/

class LBARandGenLFSR:
    ''' Implementation of LFSR to be used for sending random commands to an LBA range
        USAGE:
            block_size = 4096
            max_lba = int((128 * (1024 **4) // block_size) - 1)
            num_blocks_per_io = 4 # 16K ios in the example above
            rand_lbas = LBARandGenLFSR(max_lba, num_blocks_per_io, init_state=1, start_lba=0)
            slba = lbas.next() # call until slba == lbas.initial_state

        NOTES:
            Since 0 is never returned by an LFSR but is a valid LBA, it is
            always returned as the last value in the sequece
    '''
    def __init__(self, max_lba, num_blocks_per_io, initial_state=237, start_lba=0):
        ''' max_lba: largest LBA to return
            num_blocks_per_io: how many blocks per lba to be used
            initial_state: seed for the LFSR
            start_lba: smallest lba to return. If used, the number of
              lbas returned will be in the max_lba - start_lba range
        '''
        self.max_lba = max_lba - num_blocks_per_io
        self.num_blocks_per_io = num_blocks_per_io
        self.start_lba = start_lba

        # Make sure the initial value is a valid lba
        self.initial_state = initial_state

        # Max value
        assert self.start_lba < self.max_lba, (
            'Max lba 0x{:x} must be greater than start lba 0x{:x}'.format(
                self.max_lba, self.start_lba))
        self.max_value = (self.max_lba - start_lba) // num_blocks_per_io

        # Initial state
        assert self.initial_state < self.max_value, (
            'Invalid initial state value: {}. Must be less than {}'.format(
                self.initial_state, self.max_value))
        assert self.initial_state != 0, (
            'Invalid initial state value: {}. Cannot be 0!!'.format(
                self.initial_state))
        self.state = self.initial_state

        # Figure out the max number of bits in the lfsr for the number of LBAs
        self.num_bits = len(bin(self.max_value)[2:])
        self.next = self.get_lfsr_func()

        # Keep track of the number of generated values
        self.period = 0
        self.complete = False

    def reset(self):
        self.state = self.initial_state
        self.period = 0
        self.complete = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.complete:
            raise StopIteration()

        if self.state == self.initial_state and self.period > 0:
            self.complete = True
            ret = 0 + self.start_lba
        else:
            ret = self.next() + self.start_lba

        return ret

    def get_lfsr_func(self):
        # Polynomials from here: https://datacipy.cz/lfsr_table.pdf

        assert self.num_bits >= 5, 'max lba has to be at least > 5 bits for the LFSR implementation'

        polys = {}
        polys[5] = [5 - p for p in [5, 4, 3, 2]]
        polys[6] = [6 - p for p in [6, 5, 3, 2]]
        polys[7] = [7 - p for p in [7, 6, 5, 4]]
        polys[8] = [8 - p for p in [8, 6, 5, 4]]
        polys[9] = [9 - p for p in [9, 8, 6, 5]]
        polys[10] = [10 - p for p in [10, 9, 7, 6]]
        polys[11] = [11 - p for p in [11, 10, 9, 7]]
        polys[12] = [12 - p for p in [12, 11, 8, 6]]
        polys[13] = [13 - p for p in [13, 12, 10, 9]]
        polys[14] = [14 - p for p in [14, 13, 11, 9]]
        polys[15] = [15 - p for p in [15, 14, 13, 11]]
        polys[16] = [16 - p for p in [16, 14, 13, 11]]
        polys[17] = [17 - p for p in [17, 16, 15, 14]]
        polys[18] = [18 - p for p in [18, 17, 16, 11]]
        polys[19] = [19 - p for p in [19, 18, 17, 14]]
        polys[20] = [20 - p for p in [20, 19, 16, 14]]
        polys[21] = [21 - p for p in [21, 20, 19, 16]]
        polys[22] = [22 - p for p in [22, 19, 18, 17]]
        polys[23] = [23 - p for p in [23, 22, 20, 18]]
        polys[24] = [24 - p for p in [24, 23, 21, 20]]
        polys[25] = [25 - p for p in [25, 24, 23, 22]]
        polys[26] = [26 - p for p in [26, 25, 24, 20]]
        polys[27] = [27 - p for p in [27, 26, 25, 22]]
        polys[28] = [28 - p for p in [28, 27, 24, 22]]
        polys[29] = [29 - p for p in [29, 28, 27, 25]]
        polys[30] = [30 - p for p in [30, 29, 26, 24]]
        polys[31] = [31 - p for p in [31, 30, 29, 28]]
        polys[32] = [32 - p for p in [32, 30, 26, 25]]
        polys[33] = [33 - p for p in [33, 32, 29, 27]]
        polys[34] = [34 - p for p in [34, 31, 30, 26]]
        polys[35] = [35 - p for p in [35, 34, 28, 27]]
        polys[36] = [36 - p for p in [36, 35, 29, 28]]
        polys[37] = [37 - p for p in [37, 36, 33, 31]]
        polys[38] = [38 - p for p in [38, 37, 33, 32]]
        polys[39] = [39 - p for p in [39, 38, 35, 32]]
        polys[40] = [40 - p for p in [40, 37, 36, 35]]

        assert self.num_bits in polys, (
            'Missing polynomial coefficients for num_bits {}'.format(self.num_bits))

        num_bits = self.num_bits
        p0, p1, p2, p3 = polys[num_bits]

        def f():
            state = self.state
            bit = (state ^ (state >> p1) ^ (state >> p2) ^ (state >> p3)) & 1
            self.state = (state >> 1) | (bit << (num_bits - 1))
            self.period += 1

            # If we are using a series that can have > max_value in it, then
            #  if we get a number that is too large just drop it and run it again
            if self.state > self.max_value:
                return f()

            return self.state * self.num_blocks_per_io

        return f
