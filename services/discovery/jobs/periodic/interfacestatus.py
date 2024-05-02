# ---------------------------------------------------------------------
# Interface Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional
import datetime
import orjson

# Third-party modules
import cachetools
from pymongo import ReadPreference
from pymongo.errors import BulkWriteError

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interface import Interface
from noc.fm.models.alarmclass import AlarmClass
from noc.inv.models.interfaceprofile import InterfaceProfile


class InterfaceStatusCheck(DiscoveryCheck):
    """
    Interface status discovery
    """

    name = "interfacestatus"
    required_script = "get_interface_status_ex"

    @staticmethod
    @cachetools.cached({})
    def get_ac_link_down() -> "AlarmClass":
        return AlarmClass.get_by_name("Network | Link | Link Down")

    def iface_alarm(self, o_status: bool, a_status: bool, iface: "Interface", timestamp):
        """
        Sync 'Network | Link | Link Down' Alarm Class to correlator
        * c - Send `clear` message for 'Link Down' message if Oper -> Up
        * ca - Send `clear` message for 'Link Down' message if Oper -> Up or Admin -> Down
        * rc - Send `raise` message if Oper -> Down and `clear` if Oper -> Up or Admin -> Down
        :param o_status:
        :param a_status:
        :param iface:
        :param timestamp:
        :return:
        """
        alarm_class = self.get_ac_link_down()
        msg = {
            "timestamp": timestamp,
            "reference": f"e:{self.object.id}:{alarm_class.id}:{iface.name}",
        }
        if iface.profile.status_discovery in {"ca", "rc"} and a_status is False:
            msg["$op"] = "clear"
            self.logger.info(
                f"Clear {alarm_class.name}: on interface {iface.name}. Reason: Admin Status Down"
            )
        if iface.profile.status_discovery in {"c", "rc", "ca"} and o_status:
            msg["$op"] = "clear"
            self.logger.info(f"Clear {alarm_class.name}: on interface {iface.name}")
        if iface.profile.status_discovery == "rc" and o_status is False and a_status is True:
            msg["$op"] = "raise"
            msg["managed_object"] = str(self.object.id)
            msg["alarm_class"] = alarm_class.name
            msg["vars"] = {"interface": iface.name}
            self.logger.info(f"Raise {alarm_class.name}: on interface {iface.name}")
        if msg.get("$op"):
            stream, partition = self.object.alarms_stream_and_partition
            self.service.publish(
                orjson.dumps(msg),
                stream=stream,
                partition=partition,
            )
            self.logger.debug(
                "Dispose: %s", orjson.dumps(msg, option=orjson.OPT_INDENT_2).decode("utf-8")
            )

    def handler(self):
        def get_interface(name) -> Optional[Interface]:
            if_name = interfaces.get(name)
            if if_name:
                return if_name
            for iname in self.object.get_profile().get_interface_names(i["interface"]):
                if_name = interfaces.get(iname)
                if if_name:
                    return if_name
            return None

        has_interfaces = self.has_capability("DB | Interfaces")
        if not has_interfaces:
            self.logger.info("No interfaces discovered. Skipping interface status check")
            return
        self.logger.info("Checking interface statuses")
        interfaces = {
            i.name: i
            for i in Interface.objects.filter(
                managed_object=self.object.id,
                type__in=["physical", "aggregated"],
                profile__in=InterfaceProfile.get_with_status_discovery(),
            ).read_preference(ReadPreference.SECONDARY_PREFERRED)
        }
        if not interfaces:
            self.logger.info("No interfaces with status discovery enabled. Skipping")
            return
        hints = [
            {"interface": key, "ifindex": v.ifindex}
            for key, v in interfaces.items()
            if getattr(v, "ifindex", None) is not None
        ] or None
        result = self.object.scripts.get_interface_status_ex(interfaces=hints)
        collection = Interface._get_collection()
        bulk = []
        now = datetime.datetime.now()
        for i in result:
            iface = get_interface(i["interface"])
            if not iface:
                continue
            old_adm_status = iface.admin_status
            kwargs = {
                "admin_status": i.get("admin_status"),
                "full_duplex": i.get("full_duplex"),
                "in_speed": i.get("in_speed"),
                "out_speed": i.get("out_speed"),
                "bandwidth": i.get("bandwidth"),
            }
            changes = self.update_if_changed(iface, kwargs, ignore_empty=list(kwargs), bulk=bulk)
            self.log_changes(f"Interface {i['interface']} status has been changed", changes)
            if iface.type == "aggregated":
                continue
            ostatus = i.get("oper_status")
            astatus = i.get("admin_status")
            if iface.oper_status != ostatus and ostatus is not None:
                self.logger.info("[%s] set oper_status to %s", i["interface"], ostatus)
                if iface.profile.status_discovery in {"c", "rc", "ca"}:
                    self.iface_alarm(ostatus, astatus, iface, timestamp=now)
                iface.set_oper_status(ostatus)
            if old_adm_status != astatus and astatus is not None:
                if iface.profile.status_discovery in {"ca", "rc"}:
                    self.iface_alarm(ostatus, astatus, iface, timestamp=now)
                if astatus is False:
                    # If admin_down send expired signal
                    iface.fire_event("off", bulk=bulk)
                else:
                    iface.fire_event("on", bulk=bulk)
            if ostatus:
                iface.fire_event("seen", bulk=bulk)
        if bulk:
            self.logger.info("Committing changes to database")
            try:
                collection.bulk_write(bulk, ordered=False)
                # 1 bulk operations complete in 0ms: inserted=0, updated=1, removed=0
                self.logger.info("Database has been synced")
            except BulkWriteError as e:
                self.logger.error("Bulk write error: '%s'", e.details)
