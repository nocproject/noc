# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed object handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

def set_down_severity(alarm):
    """
    Set alarm's down severity according to ManagedObjectProfile
    """
    if alarm.severity == alarm.alarm_class.default_severity:
        ds = alarm.managed_object.object_profile.down_severity
        if ds != alarm.severity:
            alarm.severity = ds
            alarm.log_message(
                "Changing severity to %s according to managed object profile %s" % (
                    ds, alarm.managed_object.object_profile.name),
                to_save=True)
