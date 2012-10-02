#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-sync daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
import set_env

set_env.setup(use_django=True)

if __name__ == "__main__":
    from noc.main.sync.daemon import SyncDaemon
    SyncDaemon().process_command()
