# ----------------------------------------------------------------------
# Change handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from logging import getLogger
from typing import Optional, List, Set, DefaultDict, Tuple
from collections import defaultdict

# NOC modules
from noc.models import get_model

logger = getLogger(__name__)


def on_change(changes: List[Tuple[str, str, str, Optional[List[str]]]], *args, **kwargs) -> None:
    """
    Change worker
    :param changes: List of (op, model id, item id, changed fields list)
    :param args:
    :param kwargs:
    :return:
    """
    # Datastream changes
    ds_changes: DefaultDict[str, Set[str]] = defaultdict(set)
    # Iterate over changes
    for op, model_id, item_id, changed_fields in changes:
        # Resolve item
        logger.debug("[%s|%s] Processing change: %s", model_id, item_id, op)
        model_cls = get_model(model_id)
        if not model_cls:
            logger.error("[%s|%s] Invalid model. Skipping", model_id, item_id)
            return
        if op == "delete":
            item = None
        else:
            item = model_cls.get_by_id(item_id)
            if not item:
                logger.error("[%s|%s] Missed item. Skipping", model_id, item_id)
                return
        # Process datastreams
        if hasattr(item, "iter_changed_datastream"):
            for ds_name, ds_id in item.iter_changed_datastream(
                changed_fields=set(changed_fields or [])
            ):
                ds_changes[ds_name].add(ds_id)
    # Apply datastream changes
    if ds_changes:
        apply_datastream(ds_changes)


def apply_datastream(ds_changes: DefaultDict[str, Set[str]]) -> None:
    """
    Apply datastream changes
    :param ds_changes:
    :return:
    """
    from noc.core.datastream.loader import loader

    for ds_name, items in ds_changes.items():
        ds = loader[ds_name]
        if not ds:
            logger.error("Invalid datastream: %s", ds_name)
            continue
        ds.bulk_update(sorted(items))
