#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-probe daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.pm.probe.daemon import ProbeDaemon
    ProbeDaemon().process_command()
