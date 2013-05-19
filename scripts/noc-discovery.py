#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.inv.discovery.daemon import DiscoveryDaemon
    from noc.lib.debug import error_report
    from noc.main.models import CustomField
    CustomField.install_fields()

    try:
        DiscoveryDaemon().process_command()
    except SystemExit:
        pass
    except Exception:
        error_report()
