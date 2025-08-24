# ----------------------------------------------------------------------
# Service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
import operator
from collections import defaultdict
from threading import Lock
from typing import Any, Dict, Optional, Iterable, List, Union, Tuple

# Third-party modules
import orjson
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ReferenceField,
    ListField,
    EmbeddedDocumentListField,
    LongField,
    ObjectIdField,
    IntField,
    EnumField,
    BooleanField,
)
from mongoengine.queryset.visitor import Q as m_q
import cachetools

# NOC modules
from .serviceprofile import ServiceProfile, CalculatedStatusRule
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_save, on_delete_check, on_init, tree
from noc.core.resourcegroup.decorator import resourcegroup
from noc.core.wf.decorator import workflow
from noc.core.change.decorator import change
from noc.core.service.loader import get_service
from noc.core.models.servicestatus import Status
from noc.core.models.serviceinstanceconfig import InstanceType, ServiceInstanceConfig
from noc.core.models.inputsources import InputSource
from noc.core.mx import MessageType, send_message, MessageMeta, get_subscription_id
from noc.core.caps.decorator import capabilities
from noc.core.caps.types import CapsValue
from noc.core.etl.remotemappings import mappings
from noc.core.diagnostic.types import DiagnosticConfig
from noc.core.diagnostic.decorator import diagnostic
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.remotemappingsitem import RemoteMappingItem
from noc.main.models.label import Label
from noc.main.models.pool import Pool
from noc.sla.models.slaprobe import SLAProbe
from noc.wf.models.state import State
from noc.inv.models.capsitem import CapsItem
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.diagnosticitem import DiagnosticItem
from noc.sa.models.serviceinstance import ServiceInstance
from noc.pm.models.agent import Agent
from noc.config import config

logger = logging.getLogger(__name__)

id_lock = Lock()
_path_cache = cachetools.TTLCache(maxsize=100, ttl=60)
SVC_REF_PREFIX = "svc"
SVC_AC = "Service | Status | Change"


class Instance(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    name_template = StringField()
    pool: "Pool" = PlainReferenceField(Pool, required=False)
    port_range = StringField()


class ServiceStatusDependency(EmbeddedDocument):
    """
    Service dependency status
    Attributes:
        service: Service from dependent status
        resource_group: Group for dependent status (client)
        type: Dependency type:
            * service - for dependent service or group as client
            * group - for aggregating service or service group
            * parent - for overwrite parent dependent
            * children - for overwrite children dependent
        min_status: Min Status value receive
        max_status: Max Status value receive
        set_status: Overwrite dependent status
        weight: Dependent weight (used for calculate own status)
        ignore: Ignore Dependent for calculate own status
    """

    meta = {"strict": False, "auto_create_index": False}

    service: Optional["Service"] = PlainReferenceField("sa.Service", required=False)
    # Add to effective group, check group of client
    resource_group: Optional["ResourceGroup"] = ReferenceField(ResourceGroup, required=False)
    type = StringField(
        choices=[
            ("S", "Service (Using)"),
            ("G", "Group (UP)"),
            ("P", "Parent (UP)"),
            ("C", "Children (Down)"),
        ],
        default="S",
    )
    min_status = EnumField(Status, required=False)
    max_status = EnumField(Status, required=False)
    set_status = EnumField(Status, required=False)
    ignore = BooleanField(default=False)
    weight = IntField(min_value=0)
    # Propagate admin status

    def is_match(self) -> bool:
        if not self.service:
            return False
        if self.min_status and self.service.oper_status < self.min_status:
            return False
        if self.max_status and self.service.oper_status > self.max_status:
            return False
        return True

    # def is_match(
    #     self,
    #     profile: Optional[str] = None,
    #     status: Optional[Status] = None,
    #     weight: Optional[int] = None,
    # ) -> bool:
    #     if self.service_profile and profile != self.service_profile:
    #         return False
    #     if self.status and status == self.status:
    #         return False
    #     if self.op and self.weight and weight < self.weight:
    #         return False
    #     return True


@Label.model
@bi_sync
@tree
@on_save
@resourcegroup
@on_init
@change
@diagnostic
@workflow
@capabilities
@mappings
@on_delete_check(
    clean=[
        ("phone.PhoneNumber", "service"),
        ("sa.Service", "parent"),
    ],
    delete=[("sa.ServiceInstance", "service")],
)
class Service(Document):
    meta = {
        "collection": "noc.services",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "subscriber",
            "supplier",
            "profile",
            ("caps.capability", "caps.value"),
            "sla_probe",
            "parent",
            "order_id",
            "state",
            "effective_service_groups",
            "effective_client_groups",
            "effective_labels",
            "service_path",
        ],
    }
    profile: ServiceProfile = ReferenceField(ServiceProfile, required=True)
    name_template = StringField()
    # Creation timestamp
    ts = DateTimeField(default=datetime.datetime.now)
    # Logical state of service
    state: "State" = PlainReferenceField(State)
    # Last state change
    state_changed = DateTimeField()
    # Parent service
    parent: "Service" = ReferenceField("self", required=False)
    # Subscriber information
    subscriber: Optional[Subscriber] = ReferenceField(Subscriber, required=False)
    #
    oper_status: Status = EnumField(Status, default=Status.UNKNOWN)
    oper_status_change = DateTimeField(required=False, default=datetime.datetime.now)
    # Service oper status settings
    status_transfer_policy = StringField(
        choices=[
            ("D", "Disable"),  # Disable transfer status
            ("T", "Transparent"),  # Not transfer self status
            ("S", "Self"),  # Transfer self status
            ("P", "Profile"),
        ],
        default="P",
    )
    status_dependencies: List["ServiceStatusDependency"] = EmbeddedDocumentListField(
        ServiceStatusDependency
    )
    #
    calculate_status_function = StringField(
        choices=[
            ("D", "Disable"),
            ("P", "By Profile"),
            # MIN/MAX
            ("MX", "MAX"),
            ("MN", "MIN"),
            ("R", "By Rule"),
        ],
        default="P",
    )
    calculate_status_rules: List["CalculatedStatusRule"] = EmbeddedDocumentListField(
        CalculatedStatusRule
    )
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
    # SLAProbe
    sla_probe = PlainReferenceField(SLAProbe)
    # CPE information
    cpe_serial = StringField()
    cpe_mac = StringField()
    cpe_model = StringField()
    cpe_group = StringField()
    # Capabilities
    caps: List[CapsItem] = EmbeddedDocumentListField(CapsItem)
    diagnostics: List[DiagnosticItem] = EmbeddedDocumentListField(DiagnosticItem)
    #
    static_instances: List[Instance] = EmbeddedDocumentListField(Instance)
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
    # Remote Mappings
    mappings: List[RemoteMappingItem] = EmbeddedDocumentListField(RemoteMappingItem)

    _id_cache = cachetools.TTLCache(maxsize=500, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=500, ttl=60)
    _id_bi_id_map_cache = cachetools.LFUCache(maxsize=10000)
    _instance_cache = cachetools.TTLCache(maxsize=500, ttl=60)
    _mapping_cache = cachetools.TTLCache(maxsize=100, ttl=60)

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

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_instance_cache"))
    def get_by_instance(cls, address, port: Optional[str] = None) -> Optional["Service"]:
        if port:
            # Service.objects.filter(static_instances__match={"address": address, "port": port})
            si = ServiceInstance.objects.filter(addresses__address=address, port=port).first()
            if si:
                return si.service
        # return ServiceInstance.objects.filter(static_instances__match={"address": address, "port": 0}).first()
        si = ServiceInstance.objects.filter(addresses__address=address).first()
        return si.service if si else None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_mapping_cache"), lock=lambda _: id_lock)
    def get_by_mapping(cls, remote_system: RemoteSystem, remote_id: str) -> Optional["Service"]:
        return Service.objects.filter(
            m_q(remote_system=str(remote_system.id), remote_id=remote_id)
            | m_q(mappings__match={"remote_id": remote_id, "remote_system": remote_system.id})
        ).first()

    @classmethod
    def get_by_managed_object_id(cls, mo_id: int) -> List["Service"]:
        """"""
        return list(
            ServiceInstance.objects.filter(
                type__in=[
                    InstanceType.SERVICE_ENDPOINT,
                    InstanceType.ASSET,
                ],
                managed_object=mo_id,
            ).scalar("service")
        )

    def __str__(self):
        if self.label:
            return self.label
        return str(self.id) if self.id else "new"

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_service:
            yield "service", self.id

    @property
    def service_instances(self) -> List["ServiceInstance"]:
        return list(ServiceInstance.objects.filter(service=self.id))

    @property
    def managed_object(self):
        # to UP Path
        for si in self.service_instances:
            if si.managed_object:
                return si.managed_object

    @property
    def weight(self) -> int:
        return self.profile.weight

    @property
    def label(self) -> str:
        """Service text label"""
        if self.name_template:
            return self.name_template
        return self.description

    @property
    def interface(self):
        si = ServiceInstance.objects.filter(service=self.id, managed_object__exists=True).first()
        if si:
            return si.interface
        return

    @property
    def in_maintenance(self):
        """Check service in maintenance"""
        return False

    def check_deployed(self) -> Optional[str]:
        """Generate Workflow signal"""
        statuses = {si.is_deployed for si in self.service_instances}
        if True not in statuses:
            return
        elif False in statuses:
            return "partial"
        return "full"

    def get_nested(self) -> List["Service"]:
        """Returns list of nested services"""
        r = [self]
        for d in Service.objects.filter(parent=self):
            r += d.get_nested()
        return r

    def get_effective_managed_object(self) -> Optional[Any]:
        """Return ManagedObject to upper level"""
        path = self.get_path()
        for mo in ServiceInstance.objects.filter(
            service__in=path,
            managed_object__exists=True,
        ).scalar("managed_object"):
            if mo:
                return mo

    def on_save(self):
        # if not hasattr(self, "_changed_fields") or "nri_port" in self._changed_fields:
        #    self.unbind_interface()
        if not hasattr(self, "_changed_fields") or "parent" in self._changed_fields:
            self._refresh_managed_object()
            self.service_path = self.get_path()
            Service.objects.filter(id=self.id).update(service_path=self.service_path)
        self.sync_instances()
        # Register Final Outage
        # Refresh Service Status

    def _refresh_managed_object(self):
        from noc.sa.models.servicesummary import ServiceSummary

        mo = self.get_effective_managed_object()
        if mo:
            ServiceSummary.refresh_object(mo)

    def get_status_transfer_policy(self) -> str:
        """"""
        if self.status_transfer_policy == "P":
            return self.profile.status_transfer_policy
        return self.status_transfer_policy

    def iter_dependency_services(self, filter_match_status: bool = False) -> Iterable["Service"]:
        """Iterate over service topology, with affected statuses"""
        for item in self.status_dependencies:
            if filter_match_status and not item.is_match():
                continue
            if item.service:
                yield item.service
            if item.resource_group and item.resource_group.technology.service_model == "sa.Service":
                for svc in Service.objects.filter(effective_service_groups=item.resource_group):
                    yield svc

    def iter_dependency_status(self) -> Iterable[Tuple[Status, int]]:
        """Iterate over dependency services status"""
        for svc in Service.objects.filter(parent=self):
            p = svc.get_status_transfer_policy()
            if p == "S":
                yield svc.oper_status, svc.profile.weight
            elif p == "T":
                # Transparent
                # yield from svc.iter_dependency_status("self_only")
                ...

        for item in self.status_dependencies:
            if not item.is_match():
                continue
            yield item.service, item.service.profile.weight

    def set_oper_status(self, status: Status, timestamp: Optional[datetime.datetime] = None):
        """
        Set Operational Status for Service
        Args:
            status: New status
            timestamp: Time when status changed
        """
        # Check state on is_productive
        # if not self.state.is_productive:
        #    return
        if isinstance(status, str):
            status = Status[status]
        if self.oper_status == status:
            logger.debug("[%s] Status is same. Skipping", self.id)
            return
        logger.info(
            "[%s] Change service status: %s -> %s",
            self.id,
            self.oper_status,
            status,
        )
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        if self.oper_status_change and self.oper_status_change > timestamp:
            logger.warning(
                "[%s] New status timestamp LESS then current: '%s'. Reset timestamp",
                self.id,
                timestamp,
            )
            # timestamp = datetime.datetime.now().replace(microsecond=0)
            return
        # Register Outage, Register Maintenance
        os, ots = self.oper_status, self.oper_status_change

        self.oper_status = status
        self.oper_status_change = timestamp
        Service.objects.filter(id=self.id).update(
            oper_status=self.oper_status, oper_status_change=self.oper_status_change
        )
        # Register outage
        svcs = get_service()
        svcs.register_metrics(
            "serviceoutages",
            [
                {
                    "date": timestamp.date().isoformat(),
                    "ts": timestamp.replace(microsecond=0).isoformat(sep=" "),
                    "service": self.bi_id,
                    "service_id": str(self.id),
                    # Outage
                    "start": ots.isoformat(sep=" "),
                    "stop": self.oper_status_change.isoformat(sep=" "),
                    "from_status": {"id": os, "name": os.name},
                    "to_status": self.oper_status,
                    "in_maintenance": int(self.in_maintenance),
                }
            ],
        )
        if self.profile.is_enabled_notification:
            logger.debug("Sending status change notification")
            headers = self.get_mx_message_headers(self.effective_labels)
            msg = self.get_message_context()
            # msg["managed_object"] = self.managed_object.get_message_context()
            msg["from_status"] = {"id": os, "name": os.name}
            msg["ts"] = (timestamp.replace(microsecond=0).isoformat(),)
            send_message(
                data=msg,
                message_type=MessageType.SERVICE_STATUS_CHANGE,
                headers=headers,
            )
        # Run Service Status Refresh
        # Set Outage
        if self.profile.raise_status_alarm_policy == "D":
            return
        elif self.profile.raise_status_alarm_policy == "R" and len(self.service_path) != 1:
            # Only Root service
            return
        self.register_alarm(os)

    def get_message_context(self) -> Dict[str, Any]:
        """Service Message Ctx"""
        r = {
            "id": str(self.id),
            "label": self.label,
            "description": self.description,
            "profile": {"id": str(self.profile.id), "name": self.profile.name},
            "status": {"id": self.oper_status, "name": self.oper_status.name},
            "in_maintenance": int(self.in_maintenance),
            "agreement_id": self.agreement_id,
            "caps": self.get_caps(),
        }
        if self.remote_system:
            r["remote_system"] = {
                "id": str(self.remote_system.id),
                "name": self.remote_system.name,
            }
            r["remote_id"] = self.remote_id
        if self.profile.remote_system:
            r["profile"]["remote_system"] = {
                "id": str(self.profile.remote_system.id),
                "name": self.profile.remote_system.name,
            }
            r["profile"]["remote_id"] = self.profile.remote_id
        return r

    def get_mx_message_headers(self, labels: Optional[List[str]] = None) -> Dict[str, bytes]:
        return {
            key.config.header: key.clean_header_value(value)
            for key, value in self.message_meta.items()
        }

    @property
    def alarms_stream_and_partition(self) -> Tuple[str, int]:
        fm_pool = Pool.get_default_fm_pool()
        slots = config.get_slot_limits(f"correlator-{fm_pool}") or 1
        return f"dispose.{fm_pool.name}", self.bi_id % slots

    @property
    def message_meta(self) -> Dict[MessageMeta, Any]:
        """Message Meta for instance"""
        return {
            MessageMeta.WATCH_FOR: get_subscription_id(self),
            # MessageMeta.ADM_DOMAIN: str(self.administrative_domain.id),
            MessageMeta.PROFILE: get_subscription_id(self.profile),
            MessageMeta.GROUPS: list(self.effective_service_groups),
            MessageMeta.LABELS: list(self.effective_labels),
        }

    def get_alarm_severity(self) -> int:
        """Calculate Service alarm severity"""
        default_map = {4: 5000, 3: 4000, 2: 3000}
        if self.oper_status.value in default_map:
            return default_map[self.oper_status.value]
        return 0

    def register_alarm(self, old_status: Status):
        """
        Register Group alarm when changed Oper Status
        old_status: Previous status
        """
        # Raise alarm
        if self.oper_status > Status.UP >= old_status:
            msg = {
                "$op": "ensure_group",
                "reference": f"{SVC_REF_PREFIX}:{self.id}",
                "g_type": 3,
                "name": self.label,
                "alarm_class": SVC_AC,
                "labels": self.labels,
                "vars": {
                    "description": self.description,
                    "type": self.profile.name,
                    "service": str(self.id),
                    "from_status": old_status.name,
                    "to_status": self.oper_status.name,
                },
                "alarms": [],
            }
        elif self.oper_status <= Status.UP < old_status:
            msg = {
                "$op": "clear",
                "reference": f"{SVC_REF_PREFIX}:{self.id}",
                "timestamp": datetime.datetime.now().isoformat(),
                "message": f"Service status to {self.oper_status.name}",
            }
        else:
            return
        svc = get_service()

        stream, partition = self.alarms_stream_and_partition
        logger.info("[%s] Send alarm message: %s", self.id, msg)
        svc.publish(orjson.dumps(msg), stream=stream, partition=partition)

    def refresh_status(self):
        """Calculate Operative Status, maximum over Directed and Affected Status"""
        status = self.get_direct_status()
        status = max(status, self.get_affected_status())
        self.set_oper_status(status)

    def get_alarm_status(self) -> Status:
        """
        Calculate alarm status for service
        1. If alarm affected policy is Disabled. Return UNKNOWN
        2. Filter ActiveAlarm by affected_services field for self ID
        3. If Active Alarms is empty status UP
        4. Map ServiceInstance -> Alarms
        5. Other (w/o ServiceInstance) alarm if affected policy is 'O'
        6. Calculate Service Instance status: ServiceInstance -> (status, weight)
        7. Calculate affected alarm status: statuses -> calculate rules
        ? Default Managed Object status for Resource Group, get_status API ?
        """
        from noc.fm.models.activealarm import ActiveAlarm

        if self.profile.alarm_affected_policy == "D":
            return Status.UNKNOWN
        alarm_status = Status.UP
        instance_status = defaultdict(lambda: Status.UP)
        effective_clients = frozenset(str(x) for x in self.effective_client_groups)
        # Matcher ?
        instances: Optional[List["ServiceInstance"]] = None
        max_weight = 0
        # Calculate Alarm status
        for aa in ActiveAlarm.objects.filter(affected_services=self.id):
            # Match Rule
            rule = self.profile.get_rule_by_alarm(aa)
            if not rule:
                continue
            # Calculate Status
            status = rule.status or ServiceProfile.get_status_by_severity(aa.severity)
            logger.info(
                "[%s] Alarm status is: %s. Instance flag %s", aa, status, rule.affected_instance
            )
            if status == Status.UNKNOWN:
                continue
            if not rule.affected_instance:
                alarm_status = max(status, alarm_status)
                continue
            if (
                effective_clients
                and aa.managed_object.effective_service_groups
                and effective_clients.intersection(set(aa.managed_object.effective_service_groups))
            ):
                instance_status[aa.managed_object.id] = max(
                    instance_status[aa.managed_object.id], status
                )
            if instances is None:
                instances = [si for si in ServiceInstance.objects.filter(service=self.id)]
                max_weight = len(instances)
            for si in instances:
                if si.is_match_alarm(aa):
                    # @todo Detect Alarm Status
                    instance_status[si.id] = max(instance_status[si.id], status)
            # alarm_statuses[aa] = status
        # if not instance_status:
        # ? calculate by alarm count
        # to
        #    return alarm_status
        logger.info("[%s] Instance statuses: %s", self.id, instance_status)
        # Calculate Service Instance Status
        # Request base summary. Max Weight. Instance count, if not - set 1
        # max_weight = len(instance_status)
        if effective_clients:
            max_weight = sum(
                # @todo Add exclude instance
                r.resource_count
                for r in ResourceGroup.objects.filter(id__in=list(effective_clients))
            )
        r = {}
        for status in instance_status.values():
            if status not in r:
                r[status] = 1
            else:
                r[status] += 1
        # self.weight
        r[alarm_status] = (max_weight or 1) - sum(r.values())
        logger.debug(
            "[%s] Affected statuses: %s (MaxWeight: %s, AStatus: %s)",
            self.id,
            r,
            max_weight,
            alarm_status,
        )
        # Calculate affected status
        return self.calculate_status(r)

    def get_direct_status(self) -> Status:
        """Getting oper_status from Alarm and Diagnostics"""
        return self.get_alarm_status()

    def get_calculate_status_function(self) -> str:
        """"""
        if self.calculate_status_function == "P":
            return self.profile.calculate_status_function
        return self.calculate_status_function

    def get_effective_calculate_rules(self) -> List["CalculatedStatusRule"]:
        if self.calculate_status_function == "P":
            return self.profile.calculate_status_rules
        return self.calculate_status_rules

    def calculate_status(self, statuses: Dict[Status, int]) -> Status:
        """Calculate status by Policy"""
        if not statuses:
            return Status.UNKNOWN
        f = self.get_calculate_status_function()
        if f == "MN":
            return min(statuses.keys())
        elif f == "MX":
            return max(statuses.keys())
        logger.info("Calculate Status by Rules: %s", statuses)
        # Add Profile Rules
        for r in self.get_effective_calculate_rules():
            status = r.get_status(statuses)
            if status:
                return status
        return Status.UNKNOWN

    def get_affected_status(self) -> Status:
        """Getting operational status from dependencies services"""
        r = {}
        if self.profile.calculate_status_function == "D":
            return Status.UNKNOWN
        for status, weight in self.iter_dependency_status():
            if status == Status.UNKNOWN:
                continue
            if status not in r:
                r[status] = weight
            else:
                r[status] += weight
        if not r:
            return Status.UNKNOWN
        return self.calculate_status(r)

    @classmethod
    def get_services_by_alarm(cls, alarm) -> List[str]:
        """Return service Ids for requested alarm"""
        if alarm.alarm_class.name == SVC_AC:
            return []
        elif hasattr(alarm.components, "service") and getattr(alarm.components, "service", None):
            return [alarm.components.service.id]
        q = m_q()
        if hasattr(alarm.components, "slaprobe") and getattr(alarm.components, "slaprobe", None):
            q |= m_q(sla_probe=alarm.components.slaprobe.id)
        filters = ServiceProfile.get_alarm_service_filter(alarm)
        if not q and not filters:
            return []
        logger.info("Match Profiles: %s", filters)
        services, profile_rules = set(), []
        # Iter Alarm filters
        for instance_q, profiles in filters:
            if instance_q is None:
                profile_rules += profiles
                continue
            # Instances
            profiles = frozenset(profiles)
            for svc in ServiceInstance.objects.filter(instance_q).scalar("service"):
                if svc.profile.id not in profiles:
                    continue
                services.add(svc.id)
                if svc.service_path:
                    services |= set(svc.service_path)
        # Alarm without affected instances
        if profile_rules:
            q |= m_q(profile__in=profile_rules)
        # Check dependency
        if alarm.managed_object and alarm.managed_object.effective_service_groups and profile_rules:
            q |= m_q(
                effective_client_groups__in=alarm.managed_object.effective_service_groups,
                profile__in=profile_rules,
            )
        #
        logger.debug("Requested services by query: %s", q)
        if not q:
            return list(services)
        for (
            sid,
            path,
        ) in Service.objects.filter(
            q
        ).scalar("id", "service_path"):
            services.add(sid)
            if path:
                services |= set(path)
        return list(services)

    def unbind_interface(self):
        # from noc.inv.models.interface import Interface
        # Interface._get_collection().update_many({"service": self.id}, {"$unset": {"service": ""}})
        self._refresh_managed_object()

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

    def save_caps(self, caps: List[CapsValue], dry_run: bool = False, bulk=None):
        """"""
        from noc.inv.models.capsitem import CapsItem

        self.caps = [
            CapsItem(
                capability=c.capability, value=c.value, source=c.source.value, scope=c.scope or ""
            )
            for c in caps
        ]
        if dry_run or self._created:
            return
        self.update(caps=self.caps)
        self.sync_instances()

    def sync_instances(self):
        """Synchronize Config-base instance"""
        if self.profile.instance_policy != "C":
            return
        instances: List[ServiceInstanceConfig] = []
        for settings in self.profile.instance_settings:
            i_type = settings.get_instance_type()
            cfgs = i_type.from_settings(settings.get_config(), self, settings.name)
            if not cfgs:
                continue
            instances += cfgs
        logger.debug("[%s] Synced instances from config: %s", self, instances)
        self.update_instances(InputSource.CONFIG, instances)

    def update_instances(
        self,
        source: Union[str, InputSource],
        instances: List[ServiceInstanceConfig],
        last_update: Optional[datetime.datetime] = None,
    ):
        """Synchronize instances for source"""
        if isinstance(source, str):
            source = InputSource(source)
        processed = set()
        # Bulk
        # Check only one instances
        # By Service Group?
        for cfg in instances:
            settings = self.profile.get_instance_config(cfg.type, cfg.name)
            instance = ServiceInstance.ensure_instance(self, cfg, settings)
            # Update Data, Run sync
            instance.update_config(cfg)
            # Add Source
            instance.seen(source, last_update, dry_run=True)
            instance.save()
            processed.add(instance.id)
        # Clean Source from Instances
        for instance in ServiceInstance.objects.filter(
            service=self, sources__in=[source], id__nin=processed
        ):
            instance.unseen(source)

    def register_instance(
        self,
        type: InstanceType,
        source: InputSource = InputSource.MANUAL,
        name: Optional[str] = None,
        fqdn: Optional[str] = None,
        managed_object: Optional[Any] = None,
        # addresses
        # port
        # session_id ? register_session
    ) -> Optional["ServiceInstance"]:
        """
        Register Instance for Service

        Args:
            type: Instance type (from config)
            source: Instance source: manual, etl, discovery
            name: Instance name, for host - process name
            fqdn: Instance FQDN (for resolve address)
            managed_object: Instance Host
        """
        if source == InputSource.DISCOVERY and not managed_object:
            # To Service Discovery ?
            raise AttributeError("managed_object required for Discovery source")
        cfg = ServiceInstanceConfig.get_type(type)
        cfg = cfg.from_config(name=name, fqdn=fqdn)
        if not cfg:
            logger.warning(
                "[%s|%s] Instance Type is not allowed by Service settings", self.id, type
            )
            return None
        # Check Allowed create instance
        # Check multiple instances
        settings = self.profile.get_instance_config(type, name)
        si = ServiceInstance.ensure_instance(self, cfg, settings)
        changed = False
        # Update data
        si.seen(source)
        if si.fqdn != fqdn:
            si.fqdn = fqdn
            changed |= True
        if managed_object and si.managed_object != managed_object:
            si.refresh_managed_object(managed_object)
        elif not managed_object and si.managed_object:
            si.reset_object()
        if changed:
            si.save()
        return si

    @classmethod
    def get_component(cls, managed_object, service, **kwargs) -> Optional["Service"]:
        if service:
            return Service.get_by_id(service)

    def iter_diagnostic_configs(self) -> Iterable[DiagnosticConfig]:
        """Iterable diagnostic Config"""
        yield DiagnosticConfig(diagnostic="WEB", blocked=False)


def refresh_service_status(svc_ids: List[str]):
    logger.info("Refresh service status: %s", svc_ids)
    affected_paths = set()
    for svc in Service.objects.filter(id__in=svc_ids):
        os = svc.oper_status
        svc.refresh_status()
        if svc.parent and svc.oper_status != os:
            affected_paths.update(set(svc.parent.service_path))
    logger.info("Affected paths: %s", affected_paths)
    if not affected_paths:
        return
    # Check changed
    # Update linked
    for svc in Service.objects.filter(id__in=list(affected_paths)):
        svc.refresh_status()
