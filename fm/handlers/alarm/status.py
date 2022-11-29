# ---------------------------------------------------------------------
# Managed object status handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


def set_up(alarm):
    alarm.managed_object.set_status(True, alarm.clear_timestamp)


def set_down(alarm):
    alarm.managed_object.set_status(False, alarm.timestamp)
