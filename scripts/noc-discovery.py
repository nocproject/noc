#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
import set_env

set_env.setup(use_django=True)

if __name__ == "__main__":
    from noc.inv.discovery.daemon import DiscoveryDaemon
    from noc.lib.debug import error_report

    try:
        DiscoveryDaemon().process_command()
    except:
        error_report()
