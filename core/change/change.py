# ----------------------------------------------------------------------
# Change handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
from logging import getLogger
from typing import Optional, List, Set, DefaultDict, Tuple
from collections import defaultdict

# Third-party modules
import orjson

# NOC modules
from noc.models import get_model
from noc.core.service.loader import get_service
from noc.config import config

logger = getLogger(__name__)


def on_change(
    changes: List[Tuple[str, str, str, Optional[List[str]], Optional[float]]], *args, **kwargs
) -> None:
    """
    Change worker
    :param changes: List of (op, model id, item id, changed fields list)
    :param args:
    :param kwargs:
    :return:
    """
    # Datastream changes
    ds_changes: DefaultDict[str, Set[str]] = defaultdict(set)
    # BI Dictionary changes
    bi_dict_changes: DefaultDict[str, Set[Tuple[str, float]]] = defaultdict(set)
    # Iterate over changes
    for op, model_id, item_id, changed_fields, ts in changes:
        # Resolve item
        logger.debug("[%s|%s] Processing change: %s:%s", model_id, item_id, ts, op)
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
        # Proccess BI Dictionary
        if item:
            bi_dict_changes[model_id].add((item, ts))
    # Apply datastream changes
    if ds_changes:
        apply_datastream(ds_changes)
    #
    if bi_dict_changes:
        apply_ch_dictionary(bi_dict_changes)


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


def apply_ch_dictionary(bi_dict_changes: DefaultDict[str, Set[Tuple[str, float]]]) -> None:
    """
    Apply Clickhouse BI Dictionary
    :param bi_dict_changes:
    :return:
    """
    from noc.core.bi.dictionaries.loader import loader
    from noc.core.clickhouse.model import DictionaryModel

    svc = get_service()
    t0 = time.time()
    n_parts = len(config.clickhouse.cluster_topology.split(","))
    for dcls_name in loader:
        bi_dict_model: Optional["DictionaryModel"] = loader[dcls_name]
        if not bi_dict_model or bi_dict_model._meta.source_model not in bi_dict_changes:
            continue
        data = []
        for item, ts in bi_dict_changes[bi_dict_model._meta.source_model]:
            r = bi_dict_model.extract(item)
            if "bi_id" not in r:
                r["bi_id"] = item.bi_id
            lt = time.localtime(ts or t0)
            r["ts"] = time.strftime("%Y-%m-%d %H:%M:%S", lt)
            data += [r]

        for partition in range(0, n_parts):
            svc.publish(
                value=orjson.dumps(data),
                stream=f"ch.{bi_dict_model._meta.db_table}",
                partition=partition,
                headers={},
            )
