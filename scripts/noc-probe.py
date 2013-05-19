#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-probe daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.pm.probe import Probe
    Probe().process_command()
