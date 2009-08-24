##----------------------------------------------------------------------
## Service Activator Daemon
##----------------------------------------------------------------------
## Build python module from .proto file
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
.DEFAULT=all
.PHONY=all clean
PROTOC=protoc
TARGETS=sae_pb2.py pm_pb2.py

all:  $(TARGETS)

clean:
	rm -f $(TARGETS)

sae_pb2.py: sae.proto
	$(PROTOC) --python_out=. $<

pm_pb2.py: pm.proto
	$(PROTOC) --python_out=. $<
