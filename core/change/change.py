# ----------------------------------------------------------------------
# Change handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
import uuid
from logging import getLogger
from typing import Optional, List, Set, DefaultDict, Tuple, Dict
from collections import defaultdict

# Third-party modules
import orjson

# NOC modules
from noc.core.middleware.tls import get_user
from noc.models import get_model
from noc.core.service.loader import get_service
from noc.core.change.model import ChangeItem
from noc.config import config

logger = getLogger(__name__)


def dispose_change(changes):
    from noc.core.service.pub import publish

    for op, model_id, item_id, changed_fields, ts in changes:
        model_cls = get_model(model_id)
        item = model_cls.get_by_id(item_id)
        user = item.user if hasattr(item, "user") else str(get_user())
        item_name = item.name if hasattr(item, "name") else str(item_id)
        dc_new = {
            "change_id": str(uuid.uuid4()),
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "user": user,
            "model_name": model_id,
            "object_name": item_name,
            "op": op[0].upper(),
            "changes":  orjson.dumps(changed_fields).decode("utf-8"),
        }
        publish(orjson.dumps(dc_new), stream="ch.changes", partition=0)


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
    # BI Dictionary changes
    bi_dict_changes: DefaultDict[str, Set[Tuple[str, float]]] = defaultdict(set)
    # Sensors object
    sensors_changes: DefaultDict[str, Set[str]] = defaultdict(set)
    dispose_change(changes)
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


def apply_datastream(ds_changes: Optional[Dict[str, Set[str]]] = None) -> None:
    """
    Apply datastream changes
    :param ds_changes: Changes Items
    :return:
    """
    from noc.core.datastream.loader import loader

    ds_changes = ds_changes or {}
    for ds_name, items in ds_changes.items():
        ds = loader[ds_name]
        if not ds:
            logger.error("Invalid datastream: %s", ds_name)
            continue
        ds.bulk_update(sorted(items))


def apply_ch_dictionary(changes: List[ChangeItem]) -> None:
    """
    Apply Clickhouse BI Dictionary
    :param changes:
    :return:
    """
    from noc.core.bi.dictionaries.loader import loader
    from noc.core.clickhouse.model import DictionaryModel

    svc = get_service()
    t0 = time.time()
    n_parts = len(config.clickhouse.cluster_topology.split(","))
    bi_dict_changes = defaultdict(set)
    for item in changes:
        item = ChangeItem(**item)
        o = item.instance
        if not o:
            logger.error("[%s|%s] Missed item. Skipping", item.model_id, item.item_id)
            return
        bi_dict_changes[item.model_id].add((o, item.ts))
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


def apply_sync_sensors(changes: List[ChangeItem]) -> None:
    """

    :param changes:
    :return:
    """
    from noc.inv.models.object import Object
    from noc.inv.models.sensor import sync_object

    affected_models = set()
    affected_ids = set()
    for item in changes:
        item = ChangeItem(**item)
        fields = {cf["field"] for cf in item.changed_fields or []}
        if item.model_id == "inv.ObjectModel" and ("sensors" in fields or not fields):
            affected_models.add(item.item_id)
        elif item.model_id == "inv.Object" and ("data" in fields or not fields):
            # @todo ManagedObject address change
            affected_ids.add(item.item_id)

    if not affected_models and not affected_ids:
        return
    # Build query
    query = {}
    if affected_models:
        query["model__in"] = list(affected_models)
    if affected_ids:
        query["id__in"] = list(affected_ids)
    # Update
    for o in Object.objects.filter(**query):
        sync_object(o)
