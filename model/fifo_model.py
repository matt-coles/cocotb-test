from cocotb.result import TestFailure
from collections import deque

class fifo_model:

    def __init__(self, size, log):
        self.size = size
        self.log = log
        self.expected = deque(maxlen=size)
        self.data_out_is_x = True

    def push_to_fifo(self, val_push):
        if len(self.expected) != self.size:
            self.expected.append(val_push)
            self.log.info("Pushing to model %d, length is now: %d" % (val_push, len(self.expected)))

    def pop_from_fifo(self):
        if len(self.expected) != 0:
            self.data_out_is_x = False
            self.prev_val = self.expected.popleft()
            self.log.info("Popping from model %d, length is now: %d" % (self.prev_val, len(self.expected)))
        return self.prev_val

    def check_empty(self, empty):
        if len(self.expected) != 0 and empty.integer:
            raise TestFailure("Empty status did not match DUT, expected was %s and DUT showed %s" % (len(self.expected) == 0, bool(empty.integer)))

    def check_full(self, full):
        if len(self.expected) != self.size and full.integer:
            raise TestFailure("Full status did not match DUT")
