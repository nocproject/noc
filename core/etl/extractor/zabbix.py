# ----------------------------------------------------------------------
# Zabbix Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from typing import Iterable, Dict, Optional, List

# Third-party modules
from pydantic import BaseModel, Field
from zabbix_utils import ZabbixAPI

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
            return
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
            for hg in host.host_groups:
                labels.append(f"zabbix::hg::{hg.hormalize_name}")
            yield ManagedObject(
                id=str(host.host_id),
                name=host.name,
                profile="Generic.Host",
                pool=self.pool,
                segment=ETLMapping(value="ALL", scope="segment"),
                administrative_domain=ETLMapping(value="default", scope="adm_domain"),
                descriptrion=host.description,
                object_profile=ETLMapping(value="zabbix.network", scope="objectprofile"),
                static_service_groups=[str(hg.group_id) for hg in host.host_groups],
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
        if self.system.remote_system.last_extract_event:
            time_from = self.system.remote_system.last_extract_event
            self.logger.info("Extracting events: from %s", time_from)
        else:
            time_from = self.get_next_event_ts()
            self.logger.info("Extracting all events")
        return time_from or datetime.datetime.now() - datetime.timedelta(days=1)

    def iter_events(self, start: Optional[datetime.datetime] = None) -> Iterable[ZabbixEvent]:
        params = {
            "selectHosts": ["hostid", "host", "name"],
            # "selectRelatedObject": "extend",
            "selectTags": "extend",
            # "select_acknowledges": "extend",
            # "sortfield": ["clock"],
            # "output": ["hostid", "name"],
            "sortfield": ["clock", "eventid"],
            "sortorder": "DESC",
        }
        time_step = datetime.timedelta(hours=2)
        now = datetime.datetime.now()
        from_ts = self.get_initial_from_ts()
        self.logger.info("Extracting event from TS: %s", from_ts)
        while True:
            result = self.api.event.get(
                **params,
                time_from=int(from_ts.timestamp()),
                time_till=int((from_ts + time_step).timestamp()),
            )
            # if not result:
            #    break
            if from_ts + time_step > now:
                break
            elif not result:
                from_ts = self.get_next_event_ts(from_ts)
                from_ts -= time_step
            else:
                from_ts += time_step
            host_ids, triggers_ids = set(), set()
            # Preprocessed
            for x in result:
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
            self.targets[int(h["hostid"])] = RemoteObject(
                address=h_interface["ip"],
                name=h["name"],
                is_agent=i_type == ZabbixHostInterfaceType.AGENT,
                remote_id=h["hostid"],
            )

    @classmethod
    def get_event_class(cls, e: ZabbixEvent, labels: List[str]) -> Optional[str]:
        """"""
        if "ICMP::Unavailable" in labels:
            return "Zabbix | Host | Ping Failed"
        elif "scope::availability" in labels and "component::system" in labels:
            return "Zabbix | Agent | Not Available"
        elif "scope::availability" in labels and "component::network" in labels:
            return "Zabbix | SNMP | Not Available"
        return None

    def iter_data(self, checkpoint=None, **kwargs) -> Iterable[FMEventObject]:
        for e in self.iter_events():
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
                Var(name="ack", value=str(e.acknowledged)),
                Var(name="triggerid", value=str(tid)),
                Var(name="opdata", value=e.opdata),
            ]
            if item and item.is_snmp_interface_item:
                data += [Var(name="ifndex", value=str(item.ifindex))]
            if e.host not in self.targets:
                continue
            labels = ["remote_system::zabbix"] + [f"{t.tag}::{t.value}" for t in e.tags]
            yield FMEventObject(
                ts=e.clock,
                id=str(e.event_id),
                object=self.targets[e.host],
                severity=EventSeverity.INDETERMINATE if e.value != 0 else EventSeverity.CLEARED,
                event_class=self.get_event_class(e, labels),
                is_cleared=e.value,
                data=data,
                message=e.name,
                labels=labels,
            )
        self.api.logout()
