# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataStream change notification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import threading
import contextlib
# NOC modules
from noc.core.defer import call_later
from noc.core.datastream.loader import loader

tls = threading.local()
logger = logging.getLogger(__name__)


def register_change(ds_name, object_id):
    """
    Register single change
    :param ds_name: DataSource name
    :param object_id: Object id
    :return:
    """
    if hasattr(tls, "_datastream_changes"):
        # Within bulk_datastream_changes context
        tls._datastream_changes.add((ds_name, object_id))
    else:
        apply_change(ds_name, object_id)


@contextlib.contextmanager
def bulk_datastream_changes():
    """
    Buffer and deduplicate pending datastream changes

    Usage:

    with bulk_datastream_changes:
         ....

    :return:
    """
    # Save previous state
    last_changes = getattr(tls, "_datastream_changes", None)
    # Create new context
    tls._datastream_changes = set()
    # Perform decorated computations
    yield
    # Apply changes
    for ds_name, object_id in tls._datastream_changes:
        apply_change(ds_name, object_id)
    # Restore previous context
    if last_changes is not None:
        tls._datastream_changes = last_changes
    else:
        del tls._datastream_changes


def apply_change(ds_name, object_id):
    """

    :param ds_name:
    :param object_id:
    :return:
    """
    call_later("noc.core.datastream.change.update_object", ds_name=ds_name, object_id=object_id)


def update_object(ds_name, object_id):
    """
    Really apply DataStream updates
    :param ds_name:
    :param object_id:
    :return:
    """
    ds = loader.get_datastream(ds_name)
    if not ds:
        return
    r = ds.update_object(object_id)
    if r:
        logger.info("[%s|%s] Object has been changed", ds_name, object_id)
    else:
        logger.info("[%s|%s] Object hasn't been changed", ds_name, object_id)
