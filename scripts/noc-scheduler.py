#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-scheduler daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

if __name__ == "__main__":
    from noc.main.scheduler.daemon import SchedulerDaemon
    from noc.main.models import CustomField
    CustomField.install_fields()
    SchedulerDaemon().process_command()
