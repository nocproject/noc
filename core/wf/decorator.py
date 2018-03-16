# -*- coding: utf-8 -*-
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
        logger.info(
            "[%s] Cannot fire event '%s'. No default state. Skipping",
            self, event)
        return
    self.state.fire_event(event, self)


def fire_transition(self, transition):
    """
    Perform transition
    :param transition: Transition instance
    :return:
    """
    self.state.fire_transition(transition, self)


def document_set_state(self, state):
    """
    Set state

    * Set field
    * Perform database update
    * Invalidate caches
    * Call State on_enter_handlers
    :param self:
    :param object:
    :return:
    """
    # Direct update arguments
    set_op = {
        "state": state.id
    }
    # Set state field
    self.state = state
    # Fill expired field
    if self._has_expired:
        if state.ttl:
            self.expired = datetime.datetime.now() + datetime.timedelta(seconds=state.ttl)
        else:
            self.expired = None
        set_op["expired"] = self.expired
    # Update database directly
    # to avoid full save
    self._get_collection().update_one({
        "_id": self.id
    }, {
        "$set": set_op
    })
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


def model_set_state(self, state):
    """
    Set state

    * Set field
    * Perform database update
    * Invalidate caches
    * Call State on_enter_handlers
    :param self:
    :param object:
    :return:
    """
    # Set field
    self.state = state
    # Update database directly
    # to avoid full save
    self.__class__.objects.filter(id=self.id).update(state=str(state.id))
    # Invalidate caches
    ic_handler = getattr(self, "invalidate_caches", None)
    if ic_handler:
        ic_handler()
    # Call state on_enter_handlers
    self.state.on_enter_state(self)


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
                document, profile.workflow.name)
            return
        logger.debug("[%s] Set initial state to '%s'",
                     document, new_state.name)
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
                instance, profile.workflow.name)
            return
        logger.debug("[%s] Set initial state to '%s'",
                     instance, new_state.name)
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
    if is_document(cls):
        # MongoEngine model
        from mongoengine import signals as mongo_signals
        cls.set_state = document_set_state
        mongo_signals.post_save.connect(
            _on_document_post_save,
            sender=cls
        )
        if "last_seen" in cls._fields and "expired" in cls._fields and "first_discovered" in cls._fields:
            cls.touch = document_touch
            cls._has_expired = True
    else:
        # Django model
        from django.db.models import signals as django_signals
        cls.set_state = model_set_state
        django_signals.post_save.connect(
            _on_model_post_save,
            sender=cls
        )
    cls.fire_transition = fire_transition
    cls.fire_event = fire_event
    return cls
