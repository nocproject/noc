# ----------------------------------------------------------------------
# Zabbix Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from collections import defaultdict
from typing import Iterable, Dict, Optional, List, Tuple

# Third-party modules
from pydantic import BaseModel, Field
from zabbix_utils import ZabbixAPI, ProcessingError

# NOC modules
from noc.core.etl.extractor.base import BaseExtractor
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.core.etl.models.managedobjectprofile import ManagedObjectProfile
from noc.core.etl.models.typing import ETLMapping
from noc.core.etl.models.managedobject import ManagedObject
from noc.core.etl.models.authprofile import AuthProfile
from noc.core.etl.models.resourcegroup import ResourceGroup
from noc.core.etl.models.fmevent import FMEventObject, Var, RemoteObject
from noc.core.fm.event import EventSeverity


class MediaType(enum.IntEnum):
    EMAIL = 0
    SCRIPT = 1
    SMS = 2
    JABBER = 3
    WEBHOOK = 4
    TESTING = 5


class ItemType(enum.IntEnum):
    ZABBIX_AGENT = 0
    ZABBIX_TRAPPER = 2
    SIMPLE_CHECK = 3
    ZABBIX_INTERNAL = 5
    ZABBIX_AGENT_ACTIVE = 7
    WEB_ITEM = 9
    EXTERNAL_CHECK = 10
    DATABASE_MONITOR = 11
    IPMI_AGENT = 12
    SSH_AGENT = 13
    TELNET_AGENT = 14
    CALCULATED = 15
    JMX_AGENT = 16
    SNMP_TRAP = 17
    DEPENDENT_ITEM = 18
    HTTP_AGENT = 19
    SNMP_AGENT = 20
    SCRIPT = 21
    BROWSER = 22


class EventSource(enum.IntEnum):
    TRIGGER = 0  # event created by a trigger;
    DISCOVERED = 1  # event created by a discovery rule;
    REGISTRATION = 2  # event created by active agent AutoRegistration;
    INTERNAL = 3  # internal event;
    SERVICE = 4  # event created on service status u


class ObjectType(enum.IntEnum):
    TRIGGER = 0
    REGISTERED_HOST = 1
    REGISTERED_SERVICE = 2
    REGISTRATION = 3
    ITEM = 4
    LLD_RULE = 5
    SERVICE = 6


class ZabbixSeverity(enum.IntEnum):
    NOT_CLASSIFIED = 0
    INFORMATION = 1
    WARNING = 2
    AVERAGE = 3
    HIGH = 4
    DISASTER = 5


class ZabbixHostInterfaceType(enum.IntEnum):
    AGENT = 1
    SNMP = 2
    IPMI = 3
    JMX = 4


class ZabbixMedia(BaseModel):
    media_id: int
    type: MediaType
    topic_id: Optional[str] = None


class ZabbixTag(BaseModel):
    tag: str
    value: str
    automatic: Optional[int] = None


class ZabbixHostGroup(BaseModel):
    name: str
    group_id: int = Field(alias="groupid")
    flags: Optional[int] = None
    uuid: Optional[str] = None

    @property
    def hormalize_name(self):
        return self.name.replace("\\", "_")


class ZabbixHostInterface(BaseModel):
    interface_id: int = Field(alias="interfaceid")
    main: int
    type: ZabbixHostInterfaceType
    use_ip: int = Field(alias="useip")
    available: int
    host_id: Optional[int] = Field(None, alias="hostid")
    ip: Optional[str] = None
    dns: Optional[str] = None
    port: Optional[int] = None
    error: Optional[str] = None
    errors_from: Optional[int] = None
    disable_until: Optional[int] = None
    details: Optional[List[str]] = None


class ZabbixHost(BaseModel):
    """
    Attributes:
        name: Visible name
    """

    host_id: int = Field(alias="hostid")
    host: str
    description: str
    flags: int
    inventory_mode: int
    status: int
    tags: Optional[List[ZabbixTag]] = None
    active_available: Optional[int] = None
    monitored_by: Optional[int] = None
    name: Optional[str] = None
    ipmi_authtype: Optional[int] = None
    ipmi_password: Optional[str] = None
    ipmi_privilege: Optional[str] = None
    ipmi_username: Optional[str] = None
    maintenance_from: Optional[int] = None
    maintenance_status: Optional[int] = None
    maintenance_type: Optional[int] = None
    maintenance_id: int = Field(None, alias="hostid")
    host_groups: Optional[List[ZabbixHostGroup]] = Field(None, alias="hostgroups")
    interfaces: Optional[List[ZabbixHostInterface]] = None

    @property
    def main_interface(self) -> Optional[ZabbixHostInterface]:
        for hi in self.interfaces:
            if hi.main:
                return hi


class ZabbixEventHost(BaseModel):
    host_id: int = Field(alias="hostid")


class ZabbixEventItem(BaseModel):
    item_id: int = Field(alias="itemid")
    name: str
    type: ItemType
    key: str = Field(alias="key_")
    snmp_oid: Optional[str] = None
    triggers: List[Dict[str, str]]

    @property
    def is_snmp_interface_item(self) -> bool:
        return self.key.startswith("net.if")

    @property
    def ifindex(self) -> Optional[int]:
        """Return"""
        if self.is_snmp_interface_item and self.snmp_oid:
            return int(self.snmp_oid.rsplit(".", 1)[-1])


class ZabbixEvent(BaseModel):
    event_id: int = Field(alias="eventid")
    source: EventSource
    object: ObjectType
    object_id: int = Field(alias="objectid")
    acknowledged: int
    clock: int
    ns: int
    name: str
    value: int
    opdata: str
    severity: ZabbixSeverity
    r_eventid: Optional[int] = None
    r_clock: Optional[int] = None
    c_eventid: Optional[int] = None
    cause_eventid: Optional[int] = None
    correlationid: Optional[int] = None
    userid: Optional[int] = None
    suppressed: Optional[int] = None
    urls: Optional[List[str]] = None
    tags: Optional[List[ZabbixTag]] = None
    relatedObject: Optional[Dict[str, str]] = None
    hosts: Optional[List[ZabbixEventHost]] = None

    @property
    def created(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.clock)

    @property
    def host(self) -> Optional[int]:
        if not self.hosts:
            return None
        return self.hosts[0].host_id


class ZabbixRemoteSystem(BaseRemoteSystem):
    """
    Configuration variables (Main -> Setup -> Remote System -> Environments)
    API_URL - URL zabbix web interface
    API_USER - username for ro access to device
    API_PASSWORD - password for user access
    GROUPS_FILTER - list groups for extract
    """


class ZabbixExtractor(BaseExtractor):
    def __init__(self, system):
        super().__init__(system)
        self.url = self.config.get("API_URL", None)
        self.token = self.config.get("API_TOKEN", None)
        self.groups_filter = self.config.get("GROUPS_FILTER", [])
        self.user = self.config.get("API_USER", None)
        self.passw = self.config.get("API_PASSWORD", None)
        self.scheme = self.config.get("DEFAULT_SCHEME", None) or "2"
        self.pool = self.config.get("DEFAULT_POOL", None) or "default"
        self.api = ZabbixAPI(url=self.url, token=self.token, validate_certs=False)


@ZabbixRemoteSystem.extractor
class ZBAuthProfileExtractor(BaseExtractor):
    """ """

    name = "authprofile"
    model = AuthProfile
    data = [
        AuthProfile(id="ZB.AUTO", name="ZB.AUTO", type="G", snmp_ro="public"),
    ]


@ZabbixRemoteSystem.extractor
class ZabbixManagedObjectProfileExtractor(BaseExtractor):
    name = "managedobjectprofile"
    model = ManagedObjectProfile

    data = [
        ManagedObjectProfile(id="zabbix.default", name="zabbix.default", level=25),
        ManagedObjectProfile(id="zabbix.network", name="zabbix.network", level=25),
        ManagedObjectProfile(id="zb.std.sw", name="zb.std.sw", level=25),
    ]


@ZabbixRemoteSystem.extractor
class ZabbixHostGroupExtractor(ZabbixExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "resourcegroup"
    model = ResourceGroup

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ResourceGroup]:
        yield ResourceGroup(
            id="zabbix.group",
            name="Zabbix groups",
            technology="Object Group",
        )
        r = self.api.hostgroup.get()
        for group in r:
            yield ResourceGroup(
                id=str(group["groupid"]),
                name=group["name"],
                technology="Object Group",
                parent="zabbix.group",
            )
        self.api.logout()


@ZabbixRemoteSystem.extractor
class ZabbixHostExtractor(ZabbixExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "managedobject"
    model = ManagedObject

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[ManagedObject]:
        r = self.api.host.get(
            selectInterfaces=["interfaceid", "main", "type", "useip", "available", "ip"],
            selectHostGroups="extend",
            selectTags="extend",
            output=["hostid", "host", "status", "name", "flags", "description", "inventory_mode"],
        )
        for host in r:
            host = ZabbixHost.model_validate(host)
            if host.status or not host.interfaces:
                continue
            h_iface = host.main_interface
            if not h_iface:
                h_iface = host.interfaces[0]
            if not h_iface.ip or h_iface.type not in [
                ZabbixHostInterfaceType.SNMP,
                ZabbixHostInterfaceType.AGENT,
            ]:
                continue
            labels = [t.tag for t in host.tags if t.tag != "mal"]
            for hg in host.host_groups or []:
                labels.append(f"zabbix::hg::{hg.hormalize_name}")
            yield ManagedObject(
                id=str(host.host_id),
                name=host.name,
                profile="Generic.Host",
                pool="default",
                segment=ETLMapping(value="ALL", scope="segment"),
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                descriptrion=host.description,
                object_profile=ETLMapping(value="zabbix.network", scope="objectprofile"),
                static_service_groups=[str(hg.group_id) for hg in host.host_groups or []],
                scheme="1",
                address=h_iface.ip,
                labels=labels,
            )
        self.api.logout()


@ZabbixRemoteSystem.extractor
class ZabbixFMEventExtractor(ZabbixExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "fmevent"
    model = FMEventObject
    DISABLE_INCREMENTAL_MERGE = True

    severity_map: Dict[ZabbixSeverity, EventSeverity] = {
        ZabbixSeverity.NOT_CLASSIFIED: EventSeverity.INDETERMINATE,  # Ignored
        ZabbixSeverity.INFORMATION: EventSeverity.INDETERMINATE,
        ZabbixSeverity.WARNING: EventSeverity.WARNING,
        ZabbixSeverity.AVERAGE: EventSeverity.MINOR,
        ZabbixSeverity.HIGH: EventSeverity.MAJOR,
        ZabbixSeverity.DISASTER: EventSeverity.CRITICAL,
    }

    # def filter(self, row) -> bool:
    #     return False

    def __init__(self, system):
        super().__init__(system)
        self.targets: Dict[int, RemoteObject] = {}
        self.items: Dict[int, ZabbixEventItem] = {}
        self.media_types: Dict[int, ZabbixMedia] = {}
        self.load_media()

    def load_media(self):
        for r in self.api.mediatype.get(output=["mediatypeid", "type", "parameters"]):
            m = ZabbixMedia.model_validate(
                {"media_id": int(r["mediatypeid"]), "type": MediaType(int(r["type"]))}
            )
            for p in r["parameters"]:
                if p["name"] == "TopicID":
                    m.topic_id = p["value"]
            self.media_types[m.media_id] = m

    def get_next_event_ts(self, from_ts: Optional[datetime.datetime] = None):
        params = {
            "sortorder": "ASC",
            "limit": 1,
            "sortfield": "clock",
        }
        if from_ts:
            params["time_from"] = int(from_ts.timestamp())
        oldest_event = self.api.event.get(**params)
        if oldest_event:
            return datetime.datetime.fromtimestamp(int(oldest_event[0]["clock"]))

    def get_initial_from_ts(self) -> datetime.datetime:
        if self.system.remote_system.last_successful_extract_event:
            time_from = self.system.remote_system.last_successful_extract_event
            self.logger.info("Initial TS from last_successful: from %s", time_from)
        else:
            time_from = self.get_next_event_ts()
            self.logger.info("Extracting all events from: %s", time_from)
        return time_from or datetime.datetime.now() - datetime.timedelta(days=1)

    def get_alerts_tags(self, alerts) -> List[Dict[str, str]]:
        """"""
        r = []
        for a in alerts:
            if not a["sendto"]:
                continue
            media = int(a["mediatypeid"])
            if media not in self.media_types:
                send_to = a["sendto"]
            elif self.media_types[media].topic_id:
                send_to = f"{a['sendto']}:{self.media_types[media].topic_id}"
            else:
                send_to = a["sendto"]
            r += [{"tag": "alerts", "value": send_to}]
        return r

    def iter_events(self, start: Optional[datetime.datetime] = None) -> Iterable[ZabbixEvent]:
        params = {
            "selectHosts": ["hostid", "name"],
            # "selectRelatedObject": "extend",
            "selectAlerts": ["sendto"],
            "selectTags": "extend",
            # "select_acknowledges": "extend",
            # "sortfield": ["clock"],
            # "output": ["hostid", "name"],
            "sortfield": ["clock", "eventid"],
            "sortorder": "DESC",
        }
        r_events_start = {}
        time_step = datetime.timedelta(hours=2)
        now = datetime.datetime.now().replace(microsecond=0)
        from_ts = start or self.get_initial_from_ts()
        self.logger.info("Extracting event from TS: %s", from_ts)
        while True:
            result = self.api.event.get(
                **params,
                time_from=int(from_ts.timestamp()),
                time_till=int((from_ts + time_step).timestamp()),
            )
            # if not result:
            #    break
            if from_ts + time_step > now and not result:
                break
            elif not result:
                from_ts = self.get_next_event_ts(from_ts)
                from_ts -= time_step
            else:
                from_ts += time_step + datetime.timedelta(seconds=1)
            host_ids, triggers_ids = set(), set()
            # Preprocessed
            for x in result:
                r_event = int(x["r_eventid"])
                if r_event:
                    r_events_start[r_event] = int(x["clock"])
                if "eventid" not in x:
                    continue
                if x["object"] != "0":
                    self.logger.warning("Event create not by trigger: %s", x)
                    continue
                if not x["hosts"]:
                    continue
                hid = int(x["hosts"][0]["hostid"])
                if hid not in self.targets:
                    host_ids.add(hid)
                tid = int(x["objectid"])
                triggers_ids.add(tid)
                # print(x["relatedObject"])
            self.logger.info("Next Event TS: %s", from_ts)
            self.update_targets(host_ids)
            self.update_event_items(triggers_ids)
            # Validate Event object
            for row in result:
                if "eventid" not in row:
                    continue
                if not row["hosts"]:
                    continue
                if row["urls"]:
                    del row["urls"]
                if int(row["eventid"]) in r_events_start:
                    row["r_clock"] = r_events_start.pop(int(row["eventid"]))
                if row.get("alerts"):
                    row["tags"] += self.get_alerts_tags(row["alerts"])
                yield ZabbixEvent.model_validate(row)

    def update_event_items(self, ids: Iterable[int]):
        new_ids = set(ids) - self.items.keys()
        if not new_ids:
            return
        for ii in self.api.item.get(
            triggerids=list(new_ids),
            selectTriggers=1,
            output=["itemid", "name", "key_", "snmp_oid", "triggers", "type", "templateid"],
        ):
            ii = ZabbixEventItem.model_validate(ii)
            for tt in ii.triggers:
                self.items[int(tt["triggerid"])] = ii

    def update_targets(self, ids: Iterable[int]):
        """Update Event Host info to Remote Object"""
        new_ids = set(ids) - self.targets.keys()
        if not new_ids:
            return
        hosts = self.api.host.get(
            selectInterfaces=["type", "ip"], hostids=list(new_ids), output=["hostid", "name"]
        )
        for h in hosts:
            if not len(h["interfaces"]):
                continue
            h_interface = h["interfaces"][0]
            i_type = ZabbixHostInterfaceType(int(h_interface["type"]))
            hostname, *_ = h["name"].split(".", 1)
            self.targets[int(h["hostid"])] = RemoteObject(
                address=h_interface["ip"],
                name=hostname,
                is_agent=i_type == ZabbixHostInterfaceType.AGENT,
                remote_id=h["hostid"],
            )

    def get_event_class(self, e: ZabbixEvent, labels: List[str]) -> Optional[str]:
        """"""
        name = e.name.strip() if e.name else ""
        if "ICMP::Unavailable" in labels or name in {
            "Unavailable by ICMP ping",
            "ICMP Нет ответа на ping",
        }:
            return "Zabbix | Host | Ping Failed"
        if "scope::availability" in labels and name and "Zabbix agent is not available" in name:
            return "Zabbix | Agent | Not Available"
        if (
            "scope::availability" in labels
            and "component::network" in labels
            and "No SNMP data collection" in name
        ):
            return "Zabbix | SNMP | Not Available"
        if name == "ICMP Высокое время ответа":
            return "Zabbix | ICMP RTT | Too High"
        return None

    def get_event_start_ts(self, event: ZabbixEvent) -> Optional[int]:
        """Resolve Start TS for old_event"""
        if not event.object_id:
            return None
        for row in self.api.event.get(
            objectids=event.object_id,
            eventid_till=event.event_id,
            limit=4,
            sortorder="DESC",
            sortfield=["eventid"],
            output=["eventid", "clock", "r_eventid"],
        ):
            r_event = int(row["r_eventid"])
            if not r_event:
                continue
            if r_event == int(event.event_id):
                return int(row["clock"])

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[FMEventObject]:
        if checkpoint:
            checkpoint = datetime.datetime.fromtimestamp(int(checkpoint)) + datetime.timedelta(
                seconds=1
            )
        non_started_ids = set()
        for e in self.iter_events(start=checkpoint):
            tid = str(e.object_id)
            item = self.items.get(e.object_id)
            if not item:
                self.register_quality_problem(
                    line=e.event_id,
                    p_class="NF_TRIGGER_ITEM",
                    message=f"Not found item for trigger: {tid}",
                    row=e,
                )
            data = [
                # Var(name="value", value=r["value"]),
                # Var(name="name", value=e.name),
                Var(name="triggerid", value=str(tid)),
                Var(name="opdata", value=e.opdata),
            ]
            if item and item.is_snmp_interface_item:
                data += [Var(name="index", value=str(item.ifindex))]
            if e.host not in self.targets:
                continue
            labels = ["remote_system::zabbix"] + [f"{t.tag}::{t.value.strip()}" for t in e.tags]
            severity = None
            if e.severity in self.severity_map:
                severity = self.severity_map[e.severity]
            if e.value == 0 and not e.r_clock:
                # Try resolve by query
                self.logger.info(
                    "[%s] Not found Start TS for closed event. Try Resolve", e.event_id
                )
                e.r_clock = self.get_event_start_ts(e)
                if not e.r_clock:
                    non_started_ids.add(e.event_id)
            yield FMEventObject(
                ts=e.clock,
                id=str(e.event_id),
                object=self.targets[e.host],
                severity=severity,
                event_class=self.get_event_class(e, labels),
                is_cleared=e.value == 0,
                data=data,
                message=e.name.strip() if e.name else None,
                labels=labels,
                start_ts=e.r_clock,
                checkpoint=str(e.clock),
            )
        self.api.logout()
        print("Non started events:", len(non_started_ids))


@ZabbixRemoteSystem.extractor
class ZabbixMetricsExtractor(ZabbixExtractor):
    """
    Extract Device Roles from NetBox
    """

    name = "metric"
    HOURS = 2

    def get_start_ts(self) -> datetime.datetime:
        if self.system.remote_system.last_successful_extract_metrics:
            self.logger.info(
                "Initial TS from last_successful: from %s",
                self.system.remote_system.last_successful_extract_metrics,
            )
            return self.system.remote_system.last_successful_extract_metrics
        return datetime.datetime.now() - datetime.timedelta(hours=self.HOURS)

    def iter_history(
        self,
        item_ids: List[str],
        start: datetime.datetime,
        end: Optional[datetime.datetime] = None,
    ) -> Iterable[Tuple[int, datetime.datetime, float, float]]:
        """Iter over Zabbix item history"""
        prev_value, prev_id = None, None
        while True:
            try:
                r = self.api.history.get(
                    time_from=int(start.timestamp()),
                    time_till=int(end.timestamp()) if end else None,
                    sortfield=["itemid", "clock"],
                    sortorder="ASC",
                    itemids=item_ids,
                    # hostids=,
                    history=0,
                )
            except ProcessingError:
                break
            if not r:
                break
            for row in r:
                clock = datetime.datetime.fromtimestamp(int(row["clock"]))
                delta, value = 0, float(row["value"])
                if prev_value and prev_id == row["itemid"]:
                    delta = value - prev_value
                yield row["itemid"], clock, value, delta
                prev_value, prev_id = value, row["itemid"]
            start += datetime.timedelta(hours=self.HOURS)

    def iter_metrics(
        self,
        item_ids: List[str],
        end_ts: Optional[datetime.datetime] = None,
        **kwargs,
    ) -> Iterable[Tuple[str, Optional[str], List[Tuple[int, float]]]]:
        """"""
        now = datetime.datetime.now().replace(microsecond=0)
        end_ts = end_ts or now
        start = self.get_start_ts()
        while item_ids:
            r = defaultdict(list)
            ids, item_ids = item_ids[:100], item_ids[100:]
            for item_id, ts, value, _ in self.iter_history(item_ids=ids, start=start, end=end_ts):
                r[item_id].append((ts, value))
            for item_id, series in r.items():
                yield item_id, None, series
