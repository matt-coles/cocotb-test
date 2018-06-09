VERILOG_SOURCES = $(PWD)/../hw-experiments/simple_fifo.v
TOPLEVEL=simple_fifo
MODULE=test_simple_fifo
include $(COCOTB)/makefiles/Makefile.inc
include $(COCOTB)/makefiles/Makefile.sim
