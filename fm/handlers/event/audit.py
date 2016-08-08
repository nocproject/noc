# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Audit handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.sa.models.interactionlog import InteractionLog
from noc.config import config


def log_cmd(event):
    """
    Log CLI command
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.command_ttl),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_COMMAND,
        text=event.vars.get("command")
    ).save()


def log_login(event):
    """
    Log login event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.login_ttl),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_LOGIN,
        text="User logged in"
    ).save()


def log_logout(event):
    """
    Log logout event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.login_ttl),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_LOGOUT,
        text="User logged out"
    ).save()


def log_reboot(event):
    """
    Log reboot event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.reboot_ttl),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_REBOOT,
        text="System rebooted"
    ).save()


def log_started(event):
    """
    Log system started event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.reboot_ttl),
        object=event.managed_object.id,
        user=None,
        op=InteractionLog.OP_STARTED,
        text="System started"
    ).save()


def log_halted(event):
    """
    Log system halted event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.reboot_ttl),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_HALTED,
        text="System halted"
    ).save()


def log_config_changed(event):
    """
    Log config changed event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=config.audit.config_ttl),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_CONFIG_CHANGED,
        text="Config changed"
    ).save()
