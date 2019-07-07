# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MongoDB wrappers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Deprecated module. Will be removed in NOC 19.5.
Use noc.core.mongo.* modules instead.
"""

# Python modules
import warnings

# Third-party modules
import mongoengine  # noqa
from mongoengine import *  # noqa
from mongoengine.base import *  # noqa
from bson import ObjectId  # noqa

# NOC modules
from noc.core.mongo.connection import connect, is_connected, get_connection, _get_db  # noqa
from noc.core.mongo.fields import (  # noqa
    PlainReferenceField,
    PlainReferenceListField,
    ForeignKeyField,
    DateField,
    RawDictField,
)

from noc.core.deprecations import RemovedInNOC1905Warning


warnings.warn(
    "noc.lib.nosql is deprecated and will be removed in NOC 19.5. Watch for pending instructions",
    RemovedInNOC1905Warning,
    stacklevel=2,
)


def auto_connect():
    """
    Fired by module import. Check if mongo database connection initialized.
    To maintain legacy behavior auto-connect when necessary and leave deprecation warning.

    :return:
    """
    if is_connected():
        return

    warnings.warn(
        "Implicit auto-connecting to MongoDB via importing noc.lib.nosql is deprecated "
        "and to be removed in NOC 19.5. "
        "Use noc.core.mongo.connection to explicit connect.",
        RemovedInNOC1905Warning,
        stacklevel=2,
    )
    connect()


# Legacy-behavior autoconnect
auto_connect()
