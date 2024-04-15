# ---------------------------------------------------------------------
# Managed Object operations
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


def reboot(event, managed_object):
    """
    Reload managed object
    """
    if not managed_object:
        return
    managed_object.scripts.reboot()
