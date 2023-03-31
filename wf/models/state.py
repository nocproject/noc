# ----------------------------------------------------------------------
# State model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional
import operator
import logging

# Third-party modules
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
)
from mongoengine.queryset.visitor import Q as m_Q
import cachetools

# NOC modules
from .workflow import Workflow
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.core.handler import get_handler
from noc.core.defer import defer
from noc.core.hash import hash_int
from noc.core.change.decorator import change
from noc.models import get_model_id, LABEL_MODELS, get_model
from noc.main.models.label import Label

logger = logging.getLogger(__name__)
id_lock = Lock()

STATE_JOB = "noc.core.wf.transition.state_job"
WIPE_JOB = "noc.sa.wipe.managedobject.wipe"


class FeatureSetting(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    enable = BooleanField(default=True)
    # raise_alarm = BooleanField(default=True)


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
        ("phone.PhoneNumber", "state"),
        ("phone.PhoneRange", "state"),
        ("pm.Agent", "state"),
        ("sa.Service", "state"),
        ("sa.ManagedObject", "state"),
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
    }
    workflow: "Workflow" = PlainReferenceField(Workflow)
    name = StringField()
    description = StringField()
    # State properties
    # Default state for workflow (starting state if not set explicitly)
    is_default = BooleanField(default=False)
    # Resource is in productive usage
    is_productive = BooleanField(default=False)
    # Resource will be wiping after expired
    wiping = BooleanField(default=False)
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
    #
    feature_settings = MapField(EmbeddedDocumentField(FeatureSetting))
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

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["State"]:
        return State.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["State"]:
        return State.objects.filter(bi_id=id).first()

    def on_save(self):
        chenged_fields = getattr(self, "_changed_fields", None)
        if (
            (chenged_fields and "is_default" in self._changed_fields) or not chenged_fields
        ) and self.is_default:
            # New default
            self.workflow.set_default_state(self)
        if (chenged_fields and "labels" in chenged_fields) or (not chenged_fields and self.labels):
            self.sync_reffered_labels()

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

        for t in Transition.objects.filter(
            m_Q(
                from_state=self.id,
                event=event,
                required_rules__labels__exists=False,
                is_active=True,
            )
            | m_Q(
                from_state=self.id,
                is_active=True,
                event=event,
                required_rules__labels__in=getattr(obj, "effective_labels", []),
            )
        ):
            if not t.is_allowed:
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

    def is_enabled_feature(self, name) -> bool:
        """
        Check diagnostic state: on/off
        :param name:
        :return:
        """
        if name in self.feature_settings:
            return self.feature_settings[name].enable
        return True

    def sync_reffered_labels(self):
        """
        Update labels on reffered models
        * filter - state=state_id
        * sync resource_group
        :return:
        """
        from noc.inv.models.resourcegroup import ResourceGroup

        for model_id in self.workflow.allowed_models:
            model = get_model(model_id)
            removed, add_labels = [], []
            for ll in Label.objects.filter(
                **{"enable_workflowstate": True, LABEL_MODELS[model_id]: True}
            ):
                # @todo more precisely
                if ll.name not in self.labels:
                    removed.append(ll.name)
            for ll.name in self.labels:
                if model.can_set_label(ll.name):
                    add_labels.append(ll.name)
            if removed:
                Label.remove_model_labels(model_id, removed, instance_filters=[("state", self.id)])
            if add_labels:
                Label.add_model_labels(model_id, add_labels, instance_filters=[("state", self.id)])
            if not hasattr(model, "effective_service_groups"):
                continue
            if removed or add_labels:
                ResourceGroup.sync_mode_groups(model_id, table_filter=[("state", str(self.id))])
        # Invalidate cache
