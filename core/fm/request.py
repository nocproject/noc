# ----------------------------------------------------------------------
# Alarm Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, Literal, List

# Third-party modules
from bson import ObjectId
from pydantic import BaseModel, Field

# NOC modules
from .enum import AlarmAction
from noc.core.models.escalationpolicy import EscalationPolicy


class ActionConfig(BaseModel):
    """
    Attributes:
        action: Run Action
        key: Action Key
        delay: Skip seconds after start
        ack: Alarm ack condition
        time_pattern: Time pattern, when allowed run
        min_severity: Min alarm severity for run
        max_retries: Max retries when Warning
        template: Template id for message
        stop_processing: Stop execute escalation if SUCCESS
        allow_fail: Allow run next actions if FAIL
    """

    action: AlarmAction
    key: Optional[str] = None
    delay: int = 0
    ack: Literal["any", "ack", "unack"] = "any"
    when: Literal["any", "on_start", "on_end"] = "any"  # Manually
    time_pattern: Optional[str] = None
    min_severity: Optional[int] = None
    # Retry until - Disable, Count, TTL
    max_retries: int = 1
    template: Optional[str] = None
    subject: Optional[str] = None
    # TT System Settings
    pre_reason: Optional[str] = None
    login: Optional[str] = None  # queue
    queue: Optional[str] = None
    promote_item_policy: Optional[str] = None
    # End options
    stop_processing: bool = False
    allow_fail: bool = True
    register_message: bool = False
    # Approve Required
    # If approve required, it suspend processing and send
    # Message to approver
    manually: bool = False
    # Manual, Group Access
    # root_only: bool = True
    policy: EscalationPolicy = EscalationPolicy.ROOT


class ActionPermission(BaseModel):
    # By Role - Role, Role -> User, Group Map (Separate Config)
    user: int
    group: int
    tt_system: str


class AllowedAction(BaseModel):
    action: AlarmAction
    login: Optional[str] = None
    access: Optional[List[ActionPermission]] = None
    stop_processing: bool = False


class ActionItem(BaseModel):
    """
    Item for actions
    Attributes:
        alarm: Alarm instance Id
        group: Alarm Group Reference
        # service: Service Id (for service-alarm escalation)
    """

    alarm: str
    group: Optional[bytes] = None
    # service: Optional[str] = None


class AlarmActionRequest(BaseModel):
    """
    Attributes:
        id: Escalation Id
        item: Escalation Item: Alarm | Group | Service
        actions: Action executed list
        start_at: start timestamp
        max_repeats: Repeat actions after last
        repeat_delay: Repeat interval
        ctx: Span Context id
        tt_system: Initial Action TT System Id
        user: Initial Action User
    """

    id: str = Field(default_factory=lambda: str(ObjectId()))
    #
    actions: List[ActionConfig]
    allowed_actions: Optional[List[AllowedAction]] = None
    start_at: Optional[datetime.datetime] = None
    item: Optional[ActionItem] = None
    # Group
    end_condition: Literal["CR", "CA", "CT", "M", "E"] = "CR"
    # policy: EscalationPolicy = EscalationPolicy.ROOT
    # tt_system
    # Repeat action
    max_repeats: int = 0
    # Repeat Until
    repeat_delay: int = 60
    # Span
    ctx: Optional[int] = None
    # From
    tt_system: Optional[str] = None
    user: Optional[int] = None

# requester (actor) - /TTsystem/User/Group
# allowed_actions - Set
# max_escalation_retries
# global_limit
# login - assign username
# Permission
# queue


# Action on TTSystem from Other TTSystem
# /Manual actions - translate to To TTSystem as ID,prepared actions (with fixed options)
# Do action by token
# actions - allowed User/Group/TTSystem. Manually
# Prepared Actions -> заполнить вызывающего и выполнить, run_by - user,job_id,action

# TTSystem Credential

# TTSystem queue - chat_id

# Actor/Requester - who request action
# On action - user
# To action - TTSystem
# on user from ttsystem


# Group, Update_items/sync_items -> state, dirty_group/update_group -> Delete/Update

# Delete Group Item?/Delete Root item | Policy
# Update Group Item/Update Root item | Policy

# Group/Group Reference -> Location,Service (from service, Caps Reference)
# Custom subject (from group)

# Alarm TTL !
