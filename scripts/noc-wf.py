#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-wf daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.wf.wf.daemon import WFDaemon
    from noc.lib.debug import error_report
    from noc.main.models import CustomField
    CustomField.install_fields()

    try:
        WFDaemon().process_command()
    except SystemExit:
        pass
    except Exception:
        error_report()
