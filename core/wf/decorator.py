# ----------------------------------------------------------------------
# @workflow decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
from typing import Optional, List

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.models import is_document, get_model_id, get_model
from noc.core.scheduler.job import Job
from noc.core.defer import call_later
from noc.core.wf.interaction import Interaction
from noc.core.change.policy import change_tracker
from noc.core.change.decorator import get_datastreams
from noc.core.change.model import ChangeField

logger = logging.getLogger(__name__)


def fire_event(self, event, bulk=None):
    """
    Perform transition using event name
    :param event: event name
    :param bulk
    :return:
    """
    if not self.state:
        logger.info("[%s] Cannot fire event '%s'. No default state. Skipping", self, event)
        return
    self.state.fire_event(event, self, bulk=bulk)


def fire_transition(self, transition):
    """
    Perform transition
    :param transition: Transition instance
    :return:
    """
    self.state.fire_transition(transition, self)


def document_set_state(
    self, state, state_changed: datetime.datetime = None, bulk=None, create=False
):
    """
    Set state

    * Set field
    * Perform database update
    * Invalidate caches
    * Call State on_enter_handlers
    :param self:
    :param state:
    :param state_changed:
    :param bulk:
    :param create: Set if assign default state
    :return:
    """
    # Direct update arguments
    set_op = {"state": state.id}
    cf = ChangeField(field="state", old=str(self.state.id) if self.state else None, new=str(state))
    prev_labels = self.state.labels if self.state else []
    # Set state field
    self.state = state
    # Set start field
    if self._has_state_changed:
        self.state_changed = state_changed or datetime.datetime.now()
        set_op["state_changed"] = self.state_changed
    # Fill expired field
    if self._has_expired:
        if state.ttl:
            self.expired = datetime.datetime.now() + datetime.timedelta(seconds=state.ttl)
        else:
            self.expired = None
        set_op["expired"] = self.expired
    # Update database directly
    # to avoid full save
    c_bulk = [UpdateOne({"_id": self.id}, {"$set": set_op})]
    # Update effective labels
    if hasattr(self, "effective_labels") and prev_labels:
        c_bulk += [UpdateOne({"_id": self.id}, {"$pullAll": {"effective_labels": prev_labels}})]
    if hasattr(self, "effective_labels") and state.labels:
        c_bulk += [
            UpdateOne(
                {"_id": self.id},
                {
                    "$addToSet": {
                        "effective_labels": {
                            "$each": [ll for ll in state.labels if self.can_set_label(ll)]
                        }
                    }
                },
            )
        ]
    # Write bulk
    if bulk is None:
        self._get_collection().bulk_write(c_bulk)
    else:
        bulk += c_bulk
    # Invalidate caches
    ic_handler = getattr(self, "invalidate_caches", None)
    if ic_handler:
        ic_handler()
    # Call state on_enter_handlers
    self.state.on_enter_state(self)
    if not create:
        change_tracker.register(
            "update",
            get_model_id(self),
            str(self.id),
            fields=[cf],
            datastreams=get_datastreams(self, {cf.field: cf.old}),
            audit=True,
        )


def document_touch(
    self, bulk: Optional[List["UpdateOne"]] = None, ts: Optional[datetime.datetime] = None
):
    if not self.state:
        logger.info("[%s] No default state. Skipping", self)
        return
    opset = {}
    ts = (ts or datetime.datetime.now()).replace(microsecond=0)
    if self.state.update_last_seen:
        opset["last_seen"] = ts
        self.last_seen = ts
    if self.state.update_expired and self.state.ttl:
        expired = ts + datetime.timedelta(seconds=self.state.ttl)
        opset["expired"] = expired
        self.expired = expired
    if not self.first_discovered:
        self.first_discovered = ts
        opset["first_discovered"] = ts
    if not opset:
        return  # No changes
    op = {"$set": opset}
    if bulk:
        # Queue to bulk operation
        bulk += [UpdateOne({"_id": self.pk}, op)]
    else:
        # Direct update
        self._get_collection().update_one({"_id": self.pk}, op)


def model_set_state(self, state, state_changed: datetime.datetime = None, bulk=None, create=False):
    """
    Set state

    * Set field
    * Perform database update
    * Invalidate caches
    * Call State on_enter_handlers
    :param self:
    :param state:
    :param state_changed:
    :param bulk:
    :param create: Set if assign default state
    :return:
    """
    # Direct update arguments
    logger.debug("[%s] Set state: %s", self.name, state)
    set_op = {"state": str(state.id)}
    cf = ChangeField(field="state", old=str(self.state.id) if self.state else None, new=str(state))
    prev_labels = self.state.labels if self.state else []
    # Set state field
    self.state = state
    # Set start field
    if self._has_state_changed:
        self.state_changed = state_changed or datetime.datetime.now()
        set_op["state_changed"] = self.state_changed
    # Fill expired field
    if self._has_expired:
        if state.ttl:
            self.expired = datetime.datetime.now() + datetime.timedelta(seconds=state.ttl)
        else:
            self.expired = None
        set_op["expired"] = self.expired
    # Update database include effective labels directly
    # to avoid full save
    if hasattr(self, "effective_labels"):
        obj_labels = set(self.effective_labels)
        if obj_labels and prev_labels:
            obj_labels -= set(prev_labels)
        state_labels = set([ll for ll in state.labels if self.can_set_label(ll)])
        if state_labels:
            obj_labels.update(state_labels)
        set_op["effective_labels"] = list(obj_labels)
    # Update record
    self.__class__.objects.filter(id=self.id).update(**set_op)
    # Invalidate caches
    ic_handler = getattr(self, "invalidate_caches", None)
    if ic_handler:
        ic_handler()
    # Call state on_enter_handlers
    self.state.on_enter_state(self)
    #
    if state.is_wiping and not state.ttl:
        self.delete()
    elif state.is_wiping:
        call_later(
            "noc.core.wf.decorator.wipe",
            delay=state.ttl or 0,
            scheduler="scheduler",
            # pool=self.escalate_managed_object.escalator_shard,
            model_id=get_model_id(self),
            oid=self.id,
        )
    # Handle became unmanaged
    if not state.is_enabled_interaction(Interaction.Alarm):
        call_later(
            "noc.core.wf.decorator.wipe_alarm",
            delay=10,
            scheduler="scheduler",
            # pool=self.escalate_managed_object.escalator_shard,
            model_id=get_model_id(self),
            oid=self.id,
        )
    if self._has_diagnostics:
        self.diagnostic.refresh_diagnostics()
        # self.diagnostic.reset_diagnostics(
        #    [d.diagnostic for d in state.iter_diagnostic_configs(self)]
        # )
    if not create:
        change_tracker.register(
            "update",
            get_model_id(self),
            str(self.id),
            fields=[cf],
            datastreams=get_datastreams(self, {cf.field: cf.old}),
            audit=True,
        )


def model_touch(
    self, bulk: Optional[List["UpdateOne"]] = None, ts: Optional[datetime.datetime] = None
):
    if not self.state:
        logger.info("[%s] No default state. Skipping", self)
        return
    opset = {}
    ts = (ts or datetime.datetime.now()).replace(microsecond=0)
    if self.state.update_last_seen:
        opset["last_seen"] = ts
        self.last_seen = ts
    if self.state.update_expired and self.state.ttl:
        expired = ts + datetime.timedelta(seconds=self.state.ttl)
        opset["expired"] = expired
        self.expired = expired
    if not self.first_discovered:
        self.first_discovered = ts
        opset["first_discovered"] = ts
    if not opset:
        return  # No changes
    if bulk is not None:
        # Queue to bulk operation
        r = self.__class__.objects.get(id=self.pk)
        for k, v in opset.items():
            setattr(r, k, v)
        bulk += [r]
    else:
        # Direct update
        self.__class__.objects.filter(id=self.pk).update(**opset)


def _on_document_post_save(sender, document, *args, **kwargs):
    if document.state is None:
        # No state, set default one
        # Get workflow
        profile = getattr(document, getattr(document, "PROFILE_LINK", "profile"))
        if not profile:
            logger.info("[%s] Cannot set default state: No profile", document)
            return
        new_state = profile.workflow.get_default_state()
        if not new_state:
            logger.info(
                "[%s] Cannot set default state: No default state for workflow %s",
                document,
                profile.workflow.name,
            )
            return
        logger.debug("[%s] Set initial state to '%s'", document, new_state.name)
        document.set_state(new_state, create=True)


def _on_model_post_save(sender, instance, *args, **kwargs):
    if instance.state is None:
        # No state, set default one
        # Get workflow
        profile = getattr(instance, getattr(instance, "PROFILE_LINK", "profile"))
        if not profile:
            logger.info("[%s] Cannot set default state: No profile", instance)
            return
        new_state = profile.workflow.get_default_state()
        if not new_state:
            logger.info(
                "[%s] Cannot set default state: No default state for workflow %s",
                instance,
                profile.workflow.name,
            )
            return
        logger.debug("[%s] Set initial state to '%s'", instance, new_state.name)
        instance.set_state(new_state, create=True)


def workflow(cls):
    """
    @workflow decorator denotes models which have .state
    field referring to WF State.

    Methods contributed to class:
    * set_state - change .state field with calling State.on_state_enter
    * fire_event - Perform transition using event name
    * fire_transition - Perform transition
    :return:
    """
    cls.fire_event = fire_event
    cls.fire_transition = fire_transition
    cls._has_workflow = True
    cls._has_expired = False
    cls._has_state_changed = False
    cls._has_diagnostics = False
    if is_document(cls):
        # MongoEngine model
        from mongoengine import signals as mongo_signals

        cls.set_state = document_set_state
        mongo_signals.post_save.connect(_on_document_post_save, sender=cls)
        if "state_changed" in cls._fields:
            cls._has_state_changed = True
        if (
            "last_seen" in cls._fields
            and "expired" in cls._fields
            and "first_discovered" in cls._fields
        ):
            cls.touch = document_touch
            cls._has_expired = True
        if "diagnostics" in cls._fields:
            cls._has_diagnostics = True
    else:
        # Django model
        from django.db.models import signals as django_signals

        cls.set_state = model_set_state
        django_signals.post_save.connect(_on_model_post_save, sender=cls)
        fields = [f.name for f in cls._meta.get_fields()]
        if "state_changed" in fields:
            cls._has_state_changed = True
        if "last_seen" in fields and "expired" in fields and "first_discovered" in fields:
            cls.touch = model_touch
            cls._has_expired = True
        if "diagnostics" in fields:
            cls._has_diagnostics = True

    cls.fire_transition = fire_transition
    cls.fire_event = fire_event
    return cls


def wipe(model_id: str, oid):
    """
    Wiping object for delay
    :param model_id:
    :param oid:
    :return:
    """
    model = get_model(model_id)
    o = model.objects.filter(id=oid).first()
    if not o:
        logger.info("[%s:%s] Object is not found. End..", model_id, oid)
        return
    elif not o.state.is_wiping:
        logger.info("[%s] Object state: %s is not enable wiping. End..", o, o.state)
        return
    logger.info("[%s] Delete...", oid)
    try:
        if model_id == "sa.ManagedObject":
            # Custom delete handler
            from noc.sa.wipe.managedobject import wipe

            wipe(o)
            return
        o.delete()
    except Exception as e:
        logger.error("[%s] Error when wipe: %s", o, str(e))
        Job.retry_after(o.state.ttl or 600)


def wipe_alarm(model_id: str, oid):
    """
    Wiping Active Alarm
    :param model_id:
    :param oid:
    :return:
    """
    # Clear alarms
    from noc.fm.models.activealarm import ActiveAlarm

    if model_id != "sa.ManagedObject":
        return
    for aa in ActiveAlarm.objects.filter(managed_object=int(oid)):
        aa.clear_alarm("Management is disabled")
