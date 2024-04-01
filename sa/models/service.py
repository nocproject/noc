# ----------------------------------------------------------------------
# Service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
import operator
from threading import Lock
from typing import Any, Dict, Optional, Iterable, List, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    LongField,
    ObjectIdField,
    EnumField,
)
from mongoengine.queryset.visitor import Q as m_q
import cachetools

# NOC modules
from .serviceprofile import ServiceProfile, Status
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_save, on_delete, on_delete_check
from noc.core.resourcegroup.decorator import resourcegroup
from noc.core.wf.decorator import workflow
from noc.core.change.decorator import change
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.sa.models.managedobject import ManagedObject
from noc.sla.models.slaprobe import SLAProbe
from noc.wf.models.state import State
from noc.inv.models.capsitem import CapsItem
from noc.inv.models.capability import Capability
from noc.pm.models.agent import Agent

logger = logging.getLogger(__name__)

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=100, ttl=60)


@Label.model
@bi_sync
@on_save
@resourcegroup
@change
@workflow
@on_delete
@on_delete_check(
    clean=[
        ("phone.PhoneNumber", "service"),
        ("inv.Interface", "service"),
        ("sa.Service", "parent"),
    ]
)
class Service(Document):
    meta = {
        "collection": "noc.services",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "subscriber",
            "supplier",
            "managed_object",
            "parent",
            "order_id",
            "agent",
            "static_service_groups",
            "effective_service_groups",
            "static_client_groups",
            "effective_client_groups",
            "labels",
            "effective_labels",
            "service_path",
        ],
    }
    profile: ServiceProfile = ReferenceField(ServiceProfile, required=True)
    # Creation timestamp
    ts = DateTimeField(default=datetime.datetime.now)
    # Logical state of service
    state: "State" = PlainReferenceField(State)
    # Last state change
    state_changed = DateTimeField()
    # Parent service
    parent = ReferenceField("self", required=False)
    # Subscriber information
    subscriber = ReferenceField(Subscriber)
    #
    oper_status = EnumField(Status, default=Status.UNKNOWN)
    oper_status_change = DateTimeField(required=False, default=datetime.datetime.now)
    #
    # maintenance
    service_path = ListField(ObjectIdField())
    # Supplier information
    supplier = ReferenceField(Supplier)
    description = StringField()
    #
    agreement_id = StringField()
    # Order Fulfillment order id
    order_id = StringField()
    stage_id = StringField()
    stage_name = StringField()
    stage_start = DateTimeField()
    # Billing contract number
    account_id = StringField()
    # Connection address
    address = StringField()
    # For port services
    managed_object = ForeignKeyField(ManagedObject)
    # NRI port id, converted by portmapper to native name
    nri_port = StringField()
    # SLAProbe
    sla_probe = PlainReferenceField(SLAProbe)
    # CPE information
    cpe_serial = StringField()
    cpe_mac = StringField()
    cpe_model = StringField()
    cpe_group = StringField()
    # Capabilities
    caps: List[CapsItem] = ListField(EmbeddedDocumentField(CapsItem))
    # Link to agent
    agent = PlainReferenceField(Agent)
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Resource groups
    static_service_groups = ListField(ObjectIdField())
    effective_service_groups = ListField(ObjectIdField())
    static_client_groups = ListField(ObjectIdField())
    effective_client_groups = ListField(ObjectIdField())

    _id_cache = cachetools.TTLCache(maxsize=500, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=500, ttl=60)
    _id_bi_id_map_cache = cachetools.LFUCache(maxsize=10000)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Service"]:
        return Service.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Service"]:
        return Service.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_bi_id_map_cache"))
    def get_bi_id_by_id(cls, sid):
        return Service.objects.filter(id=sid).scalar("bi_id").first()

    def __str__(self):
        return str(self.id) if self.id else "new service"

    def on_delete(self):
        if self.nri_port:
            self.unbind_interface()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "nri_port" in self._changed_fields:
            self.unbind_interface()
        if not hasattr(self, "_changed_fields") or "parent" in self._changed_fields:
            self._refresh_managed_object()
            self.service_path = self.get_path()
            Service.objects.filter(id=self.id).update(service_path=self.service_path)

    def _refresh_managed_object(self):
        from noc.sa.models.servicesummary import ServiceSummary

        mo = self.get_managed_object()
        if mo:
            ServiceSummary.refresh_object(mo)

    def set_oper_status(self, status: Status):
        if self.oper_status == status:
            return
        # Register Outage, Register Maintenance
        self.oper_status = status
        self.oper_status_change = datetime.datetime.now().replace(microsecond=0)
        Service.objects.filter(id=self.id).update(
            oper_status=self.oper_status, oper_status_change=self.oper_status_change
        )
        # Run Service Status Refresh
        # Set Outage

    def refresh_status(self):
        status = self.get_direct_status()
        status = max(status, self.get_affected_status())
        self.set_oper_status(status)

    def get_direct_status(self) -> Status:
        """
        Getting oper_status from Alarm and Event by alarm_filter
        :return:
        """
        from noc.fm.models.activealarm import ActiveAlarm
        from noc.fm.models.alarmseverity import AlarmSeverity

        # if not self.state.is_productive:
        #    return Status.UNKNOWN
        s_map = {}
        for num, s in enumerate(AlarmSeverity.objects.filter().order_by("-severity")):
            if num > 3:
                break
            status = Status(4 - num)
            s_map[s] = Status.UP if status < Status.SLIGHTLY_DEGRADED else status
        r = []
        for aa in ActiveAlarm.objects.filter(affected_services=self.id):
            sev = AlarmSeverity.get_severity(aa.severity)
            if sev in s_map:
                r.append(s_map[sev])
        return max(r)

    def get_affected_status(self) -> Status:
        """
        Getting oper_status from children services
        :return:
        """
        r = []
        if self.profile.status_transfer_policy == "D":
            return Status.UNKNOWN
        for svc in Service.objects.filter(parent=self):
            if self.profile.status_transfer_policy == "T" or not self.profile.status_transfer_rule:
                r.append((svc.oper_status, svc.profile.weight))
                continue
            for rule in self.profile.status_transfer_rule:
                if rule.is_match(svc) and rule.ignore:
                    break
                elif rule.is_match(svc):
                    r.append(rule.to_status)
        if not r:
            return Status.UNKNOWN
        return self.profile.calculate_status(r)

    @classmethod
    def get_services_by_alarm(cls, alarm) -> List["str"]:
        profiles = list(ServiceProfile.objects.filter(alarm_affected_policy__ne="D").scalar("id"))
        if not profiles:
            return []
        q = m_q(managed_object=alarm.managed_object)
        if hasattr(alarm.components, "slaprobe") and alarm.components.slaprobe:
            q |= m_q(sla_probe=alarm.components.slaprobe.id)
        if (
            hasattr(alarm.components, "interface")
            and alarm.components.inteface
            and alarm.components.inteface.service
        ):
            # q |= m_q(managed_object=alarm.managed_object, interface=alarm.components.inteface)
            q |= m_q(id=alarm.components.inteface.serivce)
        address = alarm.vars.get("address")
        if address:
            c = Capability.get_by_name("Channel | Address")
            # managed_object=alarm.managed_object,
            q |= m_q(caps__match={"capability": c.id, "value": address})
        if alarm.managed_object.effective_service_groups:
            q |= m_q(
                managed_object=None,
                effective_client_groups__in=alarm.managed_object.effective_service_groups,
            )
        q = m_q(profile__in=profiles) & q
        return list(Service.objects.filter(q).scalar("id"))

    def get_alarm_filter(self) -> m_q:
        """
        Getting queryset Alarm filter
        :return:
        """
        q = m_q()
        if self.managed_object:
            q &= m_q(managed_object=self.managed_object)
        if self.sla_probe:
            q &= m_q(vars__slaprobe=self.sla_probe.id)
        # Interfaceiface = I
        return q

    def unbind_interface(self):
        from noc.inv.models.interface import Interface

        Interface._get_collection().update_many({"service": self.id}, {"$unset": {"service": ""}})
        self._refresh_managed_object()

    def get_managed_object(self):
        r = self
        while r:
            if r.managed_object:
                return self.managed_object
            r = r.parent
        return None

    def get_caps(self) -> Dict[str, Any]:
        return CapsItem.get_caps(self.caps, self.profile.caps)

    def set_caps(
        self, key: str, value: Any, source: str = "manual", scope: Optional[str] = ""
    ) -> None:
        from noc.inv.models.capability import Capability

        caps = Capability.get_by_name(key)
        value = caps.clean_value(value)
        for item in self.caps:
            if str(item.capability.id) == str(caps.id):
                if not scope or item.scope == scope:
                    item.value = value
                    break
        else:
            # Insert new item
            self.caps += [CapsItem(capability=caps, value=value, source=source, scope=scope or "")]

    @cachetools.cached(_path_cache, key=lambda x: str(x.id), lock=id_lock)
    def get_path(self):
        """
        Returns list of parent segment ids
        :return:
        """
        if self.parent:
            return self.parent.get_path() + [self.id]
        return [self.id]

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_service")

    @classmethod
    def iter_effective_labels(cls, instance: "Service") -> Iterable[List[str]]:
        yield list(instance.labels or [])
        yield list(ServiceProfile.iter_lazy_labels(instance.profile))

    def get_effective_agent(self) -> Optional[Agent]:
        """
        Find effective agent for service
        :return:
        """
        svc = self
        while svc:
            if svc.agent:
                return svc.agent
            svc = svc.parent
        return None

    def get_message_context(self) -> Dict[str, Any]:
        return {"caps": self.get_caps()}

    @property
    def in_maintenance(self):
        """
        Check service in maintenance
        :return:
        """
        return False

    @property
    def weight(self) -> int:
        return self.profile.weight


def refresh_service_status(svc_ids: List[str]):
    logger.info("[%s] Refresh service status: %s", svc_ids)
    for svc in Service.objects.filter(id__in=svc_ids):
        svc.refresh_status()
