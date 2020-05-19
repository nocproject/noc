# ----------------------------------------------------------------------
# DataStream change notification
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import contextlib
from collections import defaultdict

# NOC modules
from noc.core.defer import call_later
from noc.core.datastream.loader import loader

tls = threading.local()


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
    apply_changes(list(set(tls._datastream_changes)))
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


def do_changes(changes):
    """
    Change calculation worker
    :param changes: List of datastream name, object id
    :return:
    """
    # Compact and organize datastreams
    datastreams = defaultdict(set)
    for ds_name, object_id in changes:
        datastreams[ds_name].add(object_id)
    # Apply batches
    for ds_name in datastreams:
        ds = loader[ds_name]
        if not ds:
            continue
        ds.bulk_update(sorted(datastreams[ds_name]))
