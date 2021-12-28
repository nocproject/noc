# ---------------------------------------------------------------------
# Interface Status check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
import operator
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

ips_lock = threading.RLock()


class InterfaceStatusCheck(DiscoveryCheck):
    """
    Interface status discovery
    """

    name = "interfacestatus"
    required_script = "get_interface_status_ex"

    _ips_cache = cachetools.TTLCache(maxsize=10, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ips_cache"), lock=lambda _: ips_lock)
    def get_profiles(cls, x):
        return list(InterfaceProfile.objects.filter(status_discovery__ne="d"))

    def iface_alarm(self, ostatus, astatus, iface):
        alarm_class = AlarmClass.get_by_name("Network | Link | Link Down")
        msg = {
            "reference": f"e:{self.object.id}:{alarm_class.id}:{iface.name}",
            "alarm_class": alarm_class.name,
        }
        if iface.profile.status_discovery == "ca" and astatus is False:
            msg["$op"] = "clear"
            self.logger.info(
                f"Clear {alarm_class.name}: on interface {iface.name}. Reason: Admin Status Down"
            )
        if iface.profile.status_discovery in ["c", "rc", "ca"] and ostatus:
            msg["$op"] = "clear"
            self.logger.info(f"Clear {alarm_class.name}: on interface {iface.name}")
        if iface.profile.status_discovery == "rc" and ostatus is False and astatus is True:
            msg["$op"] = "raise"
            msg["vars"] = [
                {
                    "interface": iface.name,
                }
            ]
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
        def get_interface(name):
            if_name = interfaces.get(name)
            if if_name:
                return if_name
            for iname in self.object.get_profile().get_interface_names(i["interface"]):
                if_name = interfaces.get(iname)
                if if_name:
                    return if_name
            return None

        has_interfaces = "DB | Interfaces" in self.object.get_caps()
        if not has_interfaces:
            self.logger.info("No interfaces discovered. " "Skipping interface status check")
            return
        self.logger.info("Checking interface statuses")
        interfaces = {
            i.name: i
            for i in Interface.objects.filter(
                managed_object=self.object.id, type="physical", profile__in=self.get_profiles(None)
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
        for i in result:
            iface = get_interface(i["interface"])
            if not iface:
                continue
            kwargs = {
                "admin_status": i.get("admin_status"),
                "full_duplex": i.get("full_duplex"),
                "in_speed": i.get("in_speed"),
                "out_speed": i.get("out_speed"),
                "bandwidth": i.get("bandwidth"),
            }
            changes = self.update_if_changed(iface, kwargs, ignore_empty=list(kwargs), bulk=bulk)
            self.log_changes("Interface %s status has been changed" % i["interface"], changes)
            ostatus = i.get("oper_status")
            astatus = i.get("admin_status")
            if iface.oper_status != ostatus and ostatus is not None:
                self.logger.info("[%s] set oper status to %s", i["interface"], ostatus)
                if iface.profile.status_discovery in ["c", "rc", "ca"]:
                    self.iface_alarm(ostatus, astatus, iface)
                iface.set_oper_status(ostatus)
            if (
                iface.profile.status_discovery == ["ca"]
                and iface.admin_status != astatus
                and astatus is not None
            ):
                self.iface_alarm(ostatus, astatus, iface)

        if bulk:
            self.logger.info("Committing changes to database")
            try:
                collection.bulk_write(bulk, ordered=False)
                # 1 bulk operations complete in 0ms: inserted=0, updated=1, removed=0
                self.logger.info("Database has been synced")
            except BulkWriteError as e:
                self.logger.error("Bulk write error: '%s'", e.details)
