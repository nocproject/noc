#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.inv.discovery.daemon import DiscoveryDaemon
    from noc.lib.debug import error_report

    try:
        DiscoveryDaemon().process_command()
    except SystemExit:
        pass
    except Exception:
        error_report()
