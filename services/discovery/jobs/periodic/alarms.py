# ----------------------------------------------------------------------
# Alarms Check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
import datetime
import orjson

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activeevent import ActiveEvent


class AlarmsCheck(DiscoveryCheck):
    """
    CPE alarm discovery
    """

    name = "alarms"

    required_script = "get_alarms"

    def handler(self):
        mos = []
        self.logger.info("Checking Alarm CPEs")
        result = self.object.scripts.get_alarms()  # result get_alarms
        for r in result:
            if "path" in r:
                mos += [self.find_cpe(r["path"][0], self.object.id)]
            else:
                mos += [self.object]
        mos_id = list({mo.id for mo in mos if mo})
        # Controller Alarm
        objcet_alarms = {str(cpe["id"]): cpe for cpe in result}
        # System Events
        system_alarms = {
            str(a.raw_vars["id"]): a
            for a in ActiveEvent.objects.filter(
                managed_object__in=mos_id, source="other", raw_vars__id__exists=True
            )
        }
        # Search objcet alarms in system events, if objcet alarms not in system events, create!
        create_objcet_alarms = set(objcet_alarms.keys()).difference(set(system_alarms.keys()))
        # Search system events in objcet alarms, if system events not in objcet alarms, close event!
        close_objects_event = set(system_alarms.keys()).difference(set(objcet_alarms.keys()))
        # If not new/old alarms, return.
        if len(create_objcet_alarms) == 0 and len(close_objects_event) == 0:
            self.logger.debug("Is no New/Old alarms")
            return
        if len(create_objcet_alarms) != 0:
            for new_event in create_objcet_alarms:
                if "path" in objcet_alarms[new_event]:
                    managed_object = self.find_cpe(
                        objcet_alarms[new_event]["path"][0], self.object.id
                    )
                    if not managed_object:
                        managed_object = self.object
                        self.logger.warning(
                            "No object %s for alarm: \n%s"
                            % (objcet_alarms[new_event]["path"][0], objcet_alarms[new_event])
                        )
                else:
                    managed_object = self.object
                raw_vars = objcet_alarms[new_event]
                if len(raw_vars["path"]) > 1 and raw_vars["path"][1]:
                    raw_vars["slot"] = raw_vars["path"][1]
                if len(raw_vars["path"]) > 2 and raw_vars["path"][2]:
                    raw_vars["interface"] = raw_vars["path"][2]
                self.raise_event(managed_object.id, managed_object.pool.name, raw_vars)
        if len(close_objects_event) != 0:
            for close_event in close_objects_event:
                event = system_alarms[close_event]
                raw_vars = event.raw_vars
                self.raise_event(event.managed_object.id, event.managed_object.pool.name, raw_vars)
                event.mark_as_archived("Close event")
                self.logger.info("Close event %s" % event)

    @classmethod
    def find_cpe(cls, name, co_id=None):
        try:
            return ManagedObject.objects.get(name=name, controller=co_id)
        except ManagedObject.DoesNotExist:
            return None

    def raise_event(self, mo_id, pool_name, raw_vars):
        d = datetime.datetime.strptime(raw_vars["ts"], "%Y-%m-%dT%H:%M:%S")
        ts = time.mktime(d.timetuple())
        msg = {"ts": ts, "object": mo_id, "source": "other", "data": raw_vars}
        self.logger.debug("Pub Event: %s", msg)
        stream, partition = self.object.events_stream_and_partition
        self.service.publish(
            orjson.dumps(msg),
            stream=stream,
            partition=partition,
        )
