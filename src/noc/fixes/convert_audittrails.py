# ---------------------------------------------------------------------
# Convert AuditTrail to Clickhouse
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import uuid

# Third-party modules
import orjson
from collections import defaultdict

# NOC modules
from noc.main.models.audittrail import AuditTrail
from noc.core.service.pub import publish
from noc.sa.models.managedobject import ManagedObject
from noc.models import get_model
from noc.config import config

CHUNK = 70


def g_model(model_id):
    try:
        md = get_model(model_id)
        if md and hasattr(md, "name"):
            return md
    except Exception:
        return None


def fix():
    coll = AuditTrail._get_collection()
    mo_map = {}
    for mo_id, mo_name in ManagedObject.objects.filter().values_list("id", "name"):
        mo_map[str(mo_id)] = mo_name
    out = defaultdict(list)
    n_partitions = len(config.clickhouse.cluster_topology.split(","))
    for row in coll.find():
        key = int(row["object"]) % n_partitions
        if len(out[key]) > CHUNK:
            for p, data in out.items():
                if not data:
                    continue
                publish(b"\n".join(data), "ch.changes", partition=p)
            out = defaultdict(list)
        mid = row["model_id"]
        if mid == "sa.ManagedObject":
            name = mo_map.get(row["object"]) or ""
        else:
            model = get_model(mid)
            o = None
            if model and hasattr(model, "get_by_id"):
                o = model.get_by_id(int(row["object"]))
            name = str(o) if o else ""
        ts: datetime.datetime = row["timestamp"].replace(microsecond=0)
        out[key].append(
            orjson.dumps(
                {
                    "change_id": str(uuid.uuid4()),
                    "timestamp": ts.isoformat(),
                    "user": row["user"],
                    "model_name": mid,
                    "object_id": row["object"],
                    "object_name": name,
                    "op": row["op"],
                    "changes": orjson.dumps(row["changes"]).decode(),
                }
            )
        )
    for p, data in out.items():
        if not data:
            continue
        publish(b"\n".join(data), "ch.changes", partition=p)
