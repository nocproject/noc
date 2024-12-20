# ----------------------------------------------------------------------
# State model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import operator
import logging
from threading import Lock
from typing import Optional, Union, Iterable, Dict, Any

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    ReferenceField,
    LongField,
    IntField,
    MapField,
    EmbeddedDocumentField,
    UUIDField,
)
import cachetools

# NOC modules
from .workflow import Workflow
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.bi.decorator import bi_sync
from noc.core.handler import get_handler
from noc.core.defer import defer
from noc.core.hash import hash_int
from noc.core.change.decorator import change
from noc.core.wf.interaction import Interaction
from noc.core.wf.diagnostic import DiagnosticConfig, DiagnosticState, SA_DIAG, ALARM_DIAG
from noc.config import config
from noc.models import get_model_id, get_model, is_document
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label

from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

logger = logging.getLogger(__name__)
id_lock = Lock()

STATE_JOB = "noc.core.wf.transition.state_job"


class InteractionSetting(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    enable = BooleanField(default=True)
    # raise_alarm = BooleanField(default=True)

    def json_data(self) -> Dict[str, Any]:
        return {"enable": self.enable}


@bi_sync
@change
@Label.model
@on_delete_check(
    check=[
        ("wf.Transition", "from_state"),
        ("wf.Transition", "to_state"),
        ("crm.Subscriber", "state"),
        ("crm.Supplier", "state"),
        ("inv.CPE", "state"),
        ("inv.Sensor", "state"),
        ("inv.Interface", "state"),
        ("ip.Address", "state"),
        ("ip.Prefix", "state"),
        ("ip.VRF", "state"),
        ("peer.Peer", "state"),
        ("phone.PhoneNumber", "state"),
        ("phone.PhoneRange", "state"),
        ("pm.Agent", "state"),
        ("sa.Service", "state"),
        ("sa.ManagedObject", "state"),
        ("sa.DiscoveredObject", "state"),
        ("main.ModelTemplate", "default_state"),
        ("sla.SLAProbe", "state"),
        ("vc.VLAN", "state"),
        ("vc.VPN", "state"),
        ("vc.L2Domain", "state"),
    ]
)
@on_save
class State(Document):
    meta = {
        "collection": "states",
        "indexes": [{"fields": ["workflow", "name"], "unique": True}, "labels"],
        "strict": False,
        "auto_create_index": False,
        "json_collection": "wf.states",
        "json_depends_on": ["wf.workflows"],
        "json_unique_fields": [("workflow", "name")],
    }
    workflow: "Workflow" = PlainReferenceField(Workflow)
    name = StringField()
    uuid = UUIDField(binary=True)
    description = StringField()
    # State properties
    # Default state for workflow (starting state if not set explicitly)
    is_default = BooleanField(default=False)
    # Resource is in productive usage
    is_productive = BooleanField(default=False)
    # Resource will be wiping after expired
    is_wiping = BooleanField(default=False)
    # Hide record with state from list
    hide_with_state = BooleanField(default=False)
    # Discovery should update last_seen field
    update_last_seen = BooleanField(default=False)
    # State time-to-live in seconds
    # 0 - infinitive TTL
    # >0 - Set *expired* field to now + ttl
    #      Send *expired* signal when TTL expired
    # Expiration may also be delayed by *update_expired* setting
    ttl = IntField(default=0)
    # Update ttl every time when object is discovered
    update_expired = BooleanField(default=False)
    # Handler to be called on entering state
    on_enter_handlers = ListField(StringField())
    # Job to be started when entered state (jcls)
    # Job key will be <state id>-<resource model>-<resource id>
    job_handler = StringField()
    # Handlers to be called on leaving state
    on_leave_handlers = ListField(StringField())
    # WFEditor coordinates
    x = IntField(default=0)
    y = IntField(default=0)
    # Disable all interaction
    disable_all_interaction = BooleanField(default=False)
    #
    interaction_settings = MapField(EmbeddedDocumentField(InteractionSetting))
    # Labels
    labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return f"{self.workflow.name}: {self.name}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "workflow__name": self.workflow.name,
            "name": self.name,
            "uuid": self.uuid,
            "$collection": self._meta["json_collection"],
            "is_default": self.is_default,
            "is_productive": self.is_productive,
            "is_wiping": self.is_wiping,
            "hide_with_state": self.hide_with_state,
            "update_last_seen": self.update_last_seen,
            "ttl": self.ttl,
            "update_expired": self.update_expired,
            "x": self.x,
            "y": self.y,
            "disable_all_interaction": self.disable_all_interaction,
        }
        if self.description:
            r["description"] = self.description
        if self.interaction_settings:
            r["interaction_settings"] = {
                key: val.json_data() for key, val in self.interaction_settings.items()
            }
        if self.on_enter_handlers:
            r["on_enter_handlers"] = [h for h in self.on_enter_handlers]
        if self.job_handler:
            r["job_handler"] = self.job_handler
        if self.on_leave_handlers:
            r["on_leave_handlers"] = [h for h in self.on_leave_handlers]
        if self.labels:
            r["labels"] = list(self.labels)
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "workflow__name",
                "name",
                "uuid",
                "$collection",
                "description",
                "is_default",
                "is_productive",
                "is_wiping",
                "hide_with_state",
                "update_last_seen",
                "ttl",
                "update_expired",
                "on_enter_handlers",
                "job_handler",
                "on_leave_handlers",
                "x",
                "y",
                "disable_all_interaction",
                "interaction_settings",
            ],
        )

    def get_json_path(self) -> str:
        name_coll = quote_safe_path(self.workflow.name + " " + self.name)
        return os.path.join(name_coll) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["State"]:
        return State.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["State"]:
        return State.objects.filter(bi_id=bi_id).first()

    def on_save(self):
        chenged_fields = getattr(self, "_changed_fields", None)
        if (
            (chenged_fields and "is_default" in self._changed_fields) or not chenged_fields
        ) and self.is_default:
            # New default
            self.workflow.set_default_state(self)
        if (
            (chenged_fields and "is_wiping" in self._changed_fields) or not chenged_fields
        ) and self.is_wiping:
            # New default
            self.workflow.set_wiping_state(self)
        if (chenged_fields and "labels" in chenged_fields) or (not chenged_fields and self.labels):
            self.sync_referred_labels()

    def iter_changed_datastream(self, changed_fields=None):
        from noc.sa.models.managedobject import ManagedObject

        if not changed_fields or "sa.ManagedObject" not in self.workflow.allowed_models:
            return
        changed_fields = set(changed_fields)
        if {"is_wiping", "disable_all_interaction", "interaction_settings"}.intersection(
            changed_fields
        ):
            for mo_id, bi_id in ManagedObject.objects.filter(state=str(self.id)).values_list(
                "id", "bi_id"
            ):
                if config.datastream.enable_managedobject:
                    yield "managedobject", mo_id
                yield "cfgmetricsources", f"sa.ManagedObject::{bi_id}"

    def on_enter_state(self, obj):
        """
        Called when object enters state
        :param obj:
        :return:
        """
        # Process on enter handlers
        if self.on_enter_handlers:
            logger.debug("[%s|%s] Running on_enter_handlers", obj, obj.state.name)
            for hn in self.on_enter_handlers:
                try:
                    h = get_handler(str(hn))
                except ImportError as e:
                    logger.error("Error import on_enter handler: %s" % e)
                    h = None
                if h:
                    logger.debug("[%s|%s] Running %s", obj, self.name, hn)
                    h(obj)  # @todo: Catch exceptions
                else:
                    logger.debug("[%s|%s] Invalid handler %s, skipping", obj, self.name, hn)
        # Run Job handler when necessary
        if self.job_handler:
            logger.debug("[%s|%s] Running job handler %s", obj, self.name, self.job_handler)
            try:
                h = get_handler(self.job_handler)
            except ImportError as e:
                logger.error("Error import state job handler: %s" % e)
                h = None
            if h:
                defer(
                    STATE_JOB,
                    key=hash_int(obj.pk),
                    handler=self.job_handler,
                    model=get_model_id(obj),
                    object=str(obj.pk),
                )
            else:
                logger.debug(
                    "[%s|%s] Invalid job handler %s, skipping", obj, self.name, self.job_handler
                )

    def on_leave_state(self, obj):
        """
        Called when object leaves state
        :param obj:
        :return:
        """
        if self.on_leave_handlers:
            logger.debug("[%s|%s] Running on_leave_handlers", obj, self.name)
            for hn in self.on_leave_handlers:
                try:
                    h = get_handler(str(hn))
                except ImportError as e:
                    logger.error("Error import on_leave_state handler: %s" % e)
                    h = None
                if h:
                    logger.debug("[%s|%s] Running %s", obj, self.name, hn)
                    h(obj)  # @todo: Catch exceptions
                else:
                    logger.debug("[%s|%s] Invalid handler %s, skipping", obj, self.name, hn)

    def fire_transition(self, transition, obj, bulk=None):
        """
        Process transition from state
        :param transition:
        :param obj:
        :param bulk:
        :return:
        """
        assert obj.state == self
        assert transition.from_state == self
        # Leave state
        self.on_leave_state(obj)
        # Process transition
        transition.on_transition(obj)
        # Set new state
        # Raises on_enter handler
        obj.set_state(transition.to_state, bulk=bulk)

    def fire_event(self, event, obj, bulk=None):
        """
        Fire transition by event name
        :param event:
        :param obj:
        :param bulk:
        :return:
        """
        from .transition import Transition

        for t in Transition.get_active_transitions(self.id, event):
            if not t.is_allowed(labels=getattr(obj, "effective_labels", [])):
                logger.info(
                    "[%s|%s] Transition '%s' not allowed for '%s'. Skipping",
                    obj,
                    self.name,
                    t,
                    event,
                )
                continue
            self.fire_transition(t, obj, bulk=bulk)
            break
        else:
            logger.debug(
                "[%s|%s] No available transition for '%s'. Skipping", obj, self.name, event
            )

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_workflowstate")

    def clean(self):
        for mid in self.workflow.allowed_models:
            try:
                get_model(mid)
            except AssertionError:
                raise ValueError(f"Unknown model_id: {mid}")
        for ia in self.interaction_settings:
            ia = Interaction(ia)
            if self.workflow.allowed_models and ia.config.models:
                if not ia.config.models.intersection(set(self.workflow.allowed_models)):
                    raise ValueError(
                        f"Interaction {ia} not allowed for models: {self.workflow.allowed_models}"
                    )

    def is_enabled_interaction(self, interaction: Union[str, Interaction]) -> bool:
        """
        Check diagnostic state: on/off
        :param interaction:
        :return:
        """
        if self.is_wiping or self.disable_all_interaction:
            return False
        if not self.interaction_settings:
            return True
        if isinstance(interaction, str):
            interaction = Interaction(interaction.upper())
        if interaction.value in self.interaction_settings:
            return self.interaction_settings[interaction.value].enable
        return True

    def iter_diagnostic_configs(self, o=None) -> Iterable[DiagnosticConfig]:
        """
        Iterate over object diagnostics
        :param o: ManagedObject
        :return:
        """
        yield DiagnosticConfig(
            SA_DIAG,
            display_description="ServiceActivation. Allow active device interaction",
            blocked=not self.is_enabled_interaction(Interaction.ServiceActivation),
            default_state=DiagnosticState.enabled,
            run_policy="D",
            reason=(
                "Deny by Allowed interaction by State"
                if not self.is_enabled_interaction(Interaction.ServiceActivation)
                else ""
            ),
        )
        yield DiagnosticConfig(
            ALARM_DIAG,
            display_description="FaultManagement. Allow Raise Alarm on device",
            blocked=not self.is_enabled_interaction(Interaction.Alarm),
            default_state=DiagnosticState.enabled,
            run_policy="D",
            reason=(
                "Deny by Allowed interaction by State"
                if not self.is_enabled_interaction(Interaction.Alarm)
                else ""
            ),
        )

    def sync_referred_labels(self):
        """
        Update labels on referred models
        * filter - state=state_id
        * sync resource_group
        :return:
        """
        from noc.inv.models.resourcegroup import ResourceGroup

        for model_id in self.workflow.allowed_models:
            model = get_model(model_id)
            state_id = self.id
            if not is_document(model):
                # For DjangoModel, on DB save string ObjectId
                state_id = str(self.id)
            removed, add_labels = [], []
            for ll in Label.objects.filter(allow_models__all=["wf.State", model_id]):
                # @todo more precisely
                if ll.name not in self.labels:
                    removed.append(ll.name)
            for ll in self.labels:
                if model.can_set_label(ll):
                    add_labels.append(ll)
            if removed:
                Label.remove_model_labels(model_id, removed, instance_filters=[("state", state_id)])
            if add_labels:
                Label.add_model_labels(model_id, add_labels, instance_filters=[("state", state_id)])
            if not hasattr(model, "effective_service_groups"):
                continue
            if removed or add_labels:
                ResourceGroup.sync_model_groups(model_id, table_filter=[("state", state_id)])
        # Invalidate cache
