#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-pmprobe daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.pm.pmprobe.daemon import PMProbeDaemon
    PMProbeDaemon().process_command()
