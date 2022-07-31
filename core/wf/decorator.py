# ----------------------------------------------------------------------
# @workflow decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.models import is_document

logger = logging.getLogger(__name__)


def fire_event(self, event):
    """
    Perform transition using event name
    :param event: event name
    :return:
    """
    if not self.state:
        logger.info("[%s] Cannot fire event '%s'. No default state. Skipping", self, event)
        return
    self.state.fire_event(event, self)


def fire_transition(self, transition):
    """
    Perform transition
    :param transition: Transition instance
    :return:
    """
    self.state.fire_transition(transition, self)


def document_set_state(self, state, state_changed: datetime.datetime = None):
    """
    Set state

    * Set field
    * Perform database update
    * Invalidate caches
    * Call State on_enter_handlers
    :param self:
    :param state:
    :param state_changed:
    :return:
    """
    # Direct update arguments
    set_op = {"state": state.id}
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
    bulk = [UpdateOne({"_id": self.id}, {"$set": set_op})]
    # Update effective labels
    if hasattr(self, "effective_labels") and prev_labels:
        bulk += [UpdateOne({"_id": self.id}, {"$pullAll": {"effective_labels": prev_labels}})]
    if hasattr(self, "effective_labels") and state.labels:
        bulk += [
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
    self._get_collection().bulk_write(bulk)
    # Invalidate caches
    ic_handler = getattr(self, "invalidate_caches", None)
    if ic_handler:
        ic_handler()
    # Call state on_enter_handlers
    self.state.on_enter_state(self)


def document_touch(self, bulk=None):
    if not self.state:
        logger.info("[%s] No default state. Skipping", self)
        return
    opset = {}
    ts = datetime.datetime.now()
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
        self._get_collection().update({"_id": self.pk}, op)


def model_set_state(self, state, state_changed: datetime.datetime = None):
    """
    Set state

    * Set field
    * Perform database update
    * Invalidate caches
    * Call State on_enter_handlers
    :param self:
    :param state:
    :param state_changed:
    :return:
    """
    # Direct update arguments
    set_op = {"state": str(state.id)}
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


def model_touch(self, bulk=None):
    if not self.state:
        logger.info("[%s] No default state. Skipping", self)
        return
    opset = {}
    ts = datetime.datetime.now()
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
        document.set_state(new_state)


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
        instance.set_state(new_state)


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
    cls.fire_transition = fire_transition
    cls.fire_event = fire_event
    return cls
