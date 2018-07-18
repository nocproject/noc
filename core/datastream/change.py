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


def register_changes(data):
    """
    Register single change
    :param data: List of (datasource name, object id)
    :return:
    """
    if hasattr(tls, "_datastream_changes"):
        # Within bulk_datastream_changes context
        tls._datastream_changes.update(data)
    else:
        apply_changes(data)


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
    apply_changes(list(tls._datastream_changes))
    # Restore previous context
    if last_changes is not None:
        tls._datastream_changes = last_changes
    else:
        del tls._datastream_changes


def apply_changes(changes):
    """
    :param changes: List of (datastream name, object id)
    :return:
    """
    if changes:
        call_later("noc.core.datastream.change.do_changes", changes=changes)


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


def do_changes(changes):
    """
    Change calculation worker
    :param changes: List of datastream name, object id
    :return:
    """
    for ds_name, object_id in sorted(changes):
        update_object(ds_name, object_id)
