#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-collector daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.fm.collector.daemon import CollectorDaemon
    CollectorDaemon().process_command()
