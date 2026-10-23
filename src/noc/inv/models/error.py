# ---------------------------------------------------------------------
# Inventory error classes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class ConnectionError(Exception):
    """Failed to connect"""


class ModelDataError(Exception):
    """ModelInterface violation"""
