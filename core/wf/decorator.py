# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# @workflow decorator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.models import is_document


def fire_event(self, event):
    """
    Perform transition using event name
    :param event: event name
    :return:
    """
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
    # Set field
    self.state = state
    # Update database directly
    # to avoid full save
    self._get_collection().update_one({
        "_id": self.id
    }, {
        "$set": {
            "state": state.id
        }
    })
    # Invalidate caches
    ic_handler = getattr(self, "invalidate_caches", None)
    if ic_handler:
        ic_handler()
    # Call state on_enter_handlers
    self.state.on_enter_state(self)


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
    self.objects.filter(id=self.id).update(state=str(state.id))
    # Invalidate caches
    ic_handler = getattr(self, "invalidate_caches", None)
    if ic_handler:
        ic_handler()
    # Call state on_enter_handlers
    self.state.on_enter_state(self)


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
    if is_document(cls):
        # MongoEngine model
        cls.set_state = document_set_state
    else:
        # Django model
        cls.set_state = model_set_state
    cls.fire_transition = fire_transition
    cls.fire_event = fire_event
    return cls
