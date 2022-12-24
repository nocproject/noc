# ---------------------------------------------------------------------
# Convert Mongo Outages to Clickhouse
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import orjson
from collections import defaultdict

# NOC modules
from noc.fm.models.outage import Outage
from noc.core.service.pub import publish
from noc.sa.models.managedobject import ManagedObject
from noc.config import config

CHUNK = 500


def fix():
    coll = Outage._get_collection()
    mo_map = {}
    for mo_id, mo_biid, mo_adm_dom in ManagedObject.objects.filter().values_list(
        "id", "bi_id", "administrative_domain__bi_id"
    ):
        mo_map[mo_id] = {"bi_id": mo_biid, "adm_dom": mo_adm_dom}
    out = defaultdict(list)
    n_partitions = len(config.clickhouse.cluster_topology.split(","))
    for row in coll.find({"stop": {"$ne": None, "$exists": True}}):
        key = row["object"] % n_partitions
        if len(out[key]) > CHUNK:
            for p, data in out.items():
                if not data:
                    continue
                publish(b"\n".join(data), "ch.outages", partition=p)
            out = defaultdict(list)
        if row["object"] not in mo_map:
            continue
        ts: datetime.datetime = row["stop"].replace(microsecond=0)
        out[key].append(
            orjson.dumps(
                {
                    "date": ts.date().isoformat(),
                    "ts": ts.isoformat(sep=" "),
                    "managed_object": mo_map[row["object"]]["bi_id"],
                    "start": row["start"].replace(microsecond=0).isoformat(sep=" "),
                    "stop": row["stop"].replace(microsecond=0).isoformat(sep=" "),
                    "administrative_domain": mo_map[row["object"]]["adm_dom"],
                }
            )
        )
    for p, data in out.items():
        if not data:
            continue
        publish(b"\n".join(data), "ch.outages", partition=p)
