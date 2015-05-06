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
from noc.settings import config


def get_seconds(section, option):
    v = config.get(section, option)
    m = 1
    if v.endswith("h"):
        v = v[:-1]
        m = 3600
    elif v.endswith("d"):
        v = v[:-1]
        m = 24 * 3600
    elif v.endswith("w"):
        v = v[:-1]
        m = 7 * 24 * 3600
    elif v.endswith("m"):
        v = v[:-1]
        m = 30 * 24 * 3600
    elif v.endswith("y"):
        v = v[:-1]
        m = 365 * 24 * 3600
    try:
        v = int(v)
    except ValueError:
        raise "Invalid expiration option in %s:%s" % (section, option)
    return v * m

## Expiration settings
TTL_COMMAND = get_seconds("audit", "command_ttl")
TTL_LOGIN = get_seconds("audit", "login_ttl")
TTL_REBOOT = get_seconds("audit", "reboot_ttl")
TTL_CONFIG = get_seconds("audit", "config_changed_ttl")


def log_cmd(event):
    """
    Log CLI command
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_COMMAND),
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
        expire=event.timestamp + datetime.timedelta(seconds=TTL_LOGIN),
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
        expire=event.timestamp + datetime.timedelta(seconds=TTL_LOGIN),
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
        expire=event.timestamp + datetime.timedelta(seconds=TTL_REBOOT),
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
        expire=event.timestamp + datetime.timedelta(seconds=TTL_REBOOT),
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
        expire=event.timestamp + datetime.timedelta(seconds=TTL_REBOOT),
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
        expire=event.timestamp + datetime.timedelta(seconds=TTL_CONFIG),
        object=event.managed_object.id,
        user=event.vars.get("user"),
        op=InteractionLog.OP_CONFIG_CHANGED,
        text="Config changed"
    ).save()
