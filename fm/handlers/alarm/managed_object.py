# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed object handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## NOC modules
from noc.inv.models.objectuplink import ObjectUplink
from noc.fm.models.activealarm import ActiveAlarm


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


def topology_rca(alarm):
    """
    Process topology-based root cause analysys
    """
    def get_alarm(object_id):
        """
        Returns active alarm of the same class for object id.
        None - if no active alarm
        """
        return ActiveAlarm.objects.filter(
            managed_object=object_id,
            alarm_class=alarm.alarm_class.id
        ).first()

    def correlate_uplinks(alarm, uplinks):
        if not uplinks:
            return
        uplink_alarms = {}
        for o in uplinks:
            a = get_alarm(o)
            if a:
                uplink_alarms[o] = a
        if len(uplink_alarms) == len(uplinks):
            # All uplinks are faulty,
            # correlate with the last faulted
            aa = sorted(uplink_alarms.itervalues(),
                        key=operator.attrgetter("timestamp"))
            alarm.set_root(aa[-1])

    if alarm.root:
        return  # Already correlated
    o_id = alarm.managed_object.id
    ou = ObjectUplink.objects.filter(object=o_id).first()
    # Check uplinks
    if ou and ou.uplinks:
        correlate_uplinks(alarm, ou.uplinks)
    # Check downlinks
    for du in ObjectUplink.objects.filter(uplinks=o_id):
        a = get_alarm(du.object)
        if a and not a.root:
            correlate_uplinks(a, du.uplinks)
