import cocotb
import random
import model.fifo_model as fifo_model
from cocotb.monitors import Monitor
from cocotb.triggers import Timer, RisingEdge, ReadOnly
from cocotb.binary import BinaryValue
from cocotb.clock import Clock

class SignalMon(Monitor):
    def __init__(self, name, signal, clock, reset_n, callback=None, event=None):
        self.name = name
        self.signal = signal
        self.clock = clock
        self.reset_n = reset_n
        Monitor.__init__(self, callback, event)
        
    @cocotb.coroutine
    def _monitor_recv(self):
        clkedge = RisingEdge(self.clock)

        while True:
            # Capture signal at rising edge of clock
            yield clkedge
            yield ReadOnly()
            if self.reset_n.value.binstr == "1":
                vec = self.signal.value
                self._recv(vec)

@cocotb.coroutine
def push_fifo_rand(model, dut, push_when_full=False):
    while True:
        rand_wait = random.randint(0, 800000)
        if not dut.full.value.integer or push_when_full:
            val_push = BinaryValue()
            val_push.integer = random.randint(0, 65535)
            yield RisingEdge(dut.clk)
            dut.data_in = val_push.integer
            dut.push = 1
            yield RisingEdge(dut.clk)
            model.push_to_fifo(val_push)
            dut.push = 0
        yield Timer(rand_wait)

@cocotb.coroutine
def pop_fifo_rand(model, dut, pop_when_empty=False):
    while True:
        rand_wait = random.randint(0, 800000)
        if not dut.empty.value.integer or pop_when_empty:
            yield RisingEdge(dut.clk)
            dut.pop = 1
            yield RisingEdge(dut.clk)
            expected = model.pop_from_fifo()
            dut.pop = 0
            yield RisingEdge(dut.clk)
            popped = dut.data_out.value
            if not model.data_out_is_x and expected.integer != popped.integer:
                raise TestFailure("Expected %s but got %s from DUT" % (expected.binstr, popped.binstr))
        yield Timer(rand_wait)

@cocotb.coroutine
def reset_dut(dut, duration):
    dut.reset_n = 0
    yield Timer(duration)
    dut.reset_n = 1

@cocotb.test()
def random_test(dut):
    """
    Try accessing the design
    """
    model = fifo_model.fifo_model(dut.DEPTH, dut._log)
    cocotb.fork(Clock(dut.clk, 1000).start())
    cocotb.fork(reset_dut(dut, 4000))
    empty_mon = SignalMon("empty", dut.empty, dut.clk, dut.reset_n, model.check_empty)
    full_mon = SignalMon("full", dut.full, dut.clk, dut.reset_n, model.check_full)
    yield RisingEdge(dut.reset_n)
    dut._log.info("Running test! Device left reset")
    yield Timer(1000)
    cocotb.fork(push_fifo_rand(model, dut, True))
    cocotb.fork(pop_fifo_rand(model, dut, True))
    for i in range(80000):
        yield RisingEdge(dut.clk)
    dut._log.info("Stopping test!")
