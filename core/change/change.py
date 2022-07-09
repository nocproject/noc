# ----------------------------------------------------------------------
# Change handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
from logging import getLogger
from typing import Optional, List, Set, DefaultDict, Tuple, Dict
from collections import defaultdict

# Third-party modules
import orjson
from mongoengine.queryset.visitor import Q

# NOC modules
from noc.models import get_model
from noc.core.service.loader import get_service
from noc.config import config

logger = getLogger(__name__)


def on_change(
    changes: List[Tuple[str, str, str, Optional[List[Dict[str, str]]], Optional[float]]],
    *args,
    **kwargs,
) -> None:
    """
    Change worker
    :param changes: List of (op, model id, item id, changed fields list, timestamp)
    :param args:
    :param kwargs:
    :return:
    """
    # Datastream changes
    ds_changes: DefaultDict[str, Set[str]] = defaultdict(set)
    # BI Dictionary changes
    bi_dict_changes: DefaultDict[str, Set[Tuple[str, float]]] = defaultdict(set)
    # Sensors object
    sensors_changes: DefaultDict[str, Set[str]] = defaultdict(set)
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
        changed_fields = changed_fields or []
        # isinstance for old compatible format
        if changed_fields and isinstance(changed_fields[0], str):
            changed_fields_old = set(changed_fields)
        else:
            changed_fields_old = {cf["field"]: cf["old"] for cf in changed_fields or []}
        # Process datastreams
        if hasattr(item, "iter_changed_datastream"):
            for ds_name, ds_id in item.iter_changed_datastream(changed_fields=changed_fields_old):
                ds_changes[ds_name].add(ds_id)
        # Proccess BI Dictionary
        if item:
            bi_dict_changes[model_id].add((item, ts))
        # Proccess Sensors
        if model_id == "inv.ObjectModel" and (
            "sensors" in changed_fields_old or not changed_fields_old
        ):
            sensors_changes[model_id].add(item_id)
        elif model_id == "inv.Object" and ("data" in changed_fields_old or not changed_fields_old):
            # @todo ManagedObject address change
            sensors_changes[model_id].add(item_id)
    # Apply datastream changes
    if ds_changes:
        apply_datastream(ds_changes)
    #
    if bi_dict_changes:
        apply_ch_dictionary(bi_dict_changes)
    #
    if sensors_changes:
        apply_sync_sensors(sensors_changes)


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
        logger.info("[bi_dictionary] [%s] Apply changes", dcls_name)
        data = []
        for item, ts in bi_dict_changes[bi_dict_model._meta.source_model]:
            r = bi_dict_model.extract(item)
            if "bi_id" not in r:
                r["bi_id"] = item.bi_id
            lt = time.localtime(ts or t0)
            r["ts"] = time.strftime("%Y-%m-%d %H:%M:%S", lt)
            data += [orjson.dumps(r)]

        for partition in range(0, n_parts):
            svc.publish(
                value=b"\n".join(data),
                stream=f"ch.{bi_dict_model._meta.db_table}",
                partition=partition,
                headers={},
            )


def apply_sync_sensors(sensors_changes: DefaultDict[str, Set[str]]) -> None:
    """

    :param sensors_changes:
    :return:
    """
    from noc.inv.models.object import Object
    from noc.inv.models.sensor import sync_object

    query = Q()
    if "inv.ObjectModel" in sensors_changes:
        query |= Q(model__in=list(sensors_changes["inv.ObjectModel"]))
    if "inv.Object" in sensors_changes:
        query |= Q(id__in=list(sensors_changes["inv.Object"]))
    if not query:
        return

    for o in Object.objects.filter(query):
        sync_object(o)
