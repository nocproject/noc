# ---------------------------------------------------------------------
# Convert FM Events to Clickhouse
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import socket
import struct

# Third-party modules
import orjson
from collections import defaultdict

# NOC modules
from noc.fm.models.activeevent import ActiveEvent
from noc.core.service.pub import publish
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.fm.models.eventclass import EventClass
from noc.main.models.pool import Pool
from noc.config import config
from noc.core.ip import IP

CHUNK = 300
SNMP_TRPAP_OID = "1__3__6__1__6__3__1__1__4__1__0"


def fix():
    coll = ActiveEvent._get_collection()
    mo_map = {}
    for (
        mo_id,
        mo_biid,
        mo_adm_dom,
        pool,
        profile,
        address,
    ) in ManagedObject.objects.filter().values_list(
        "id", "bi_id", "administrative_domain__bi_id", "pool", "profile", "address"
    ):
        try:
            pool = Pool.get_by_id(pool).bi_id
            profile = Profile.get_by_id(profile).bi_id
        except AttributeError:
            continue
        address = struct.unpack("!I", socket.inet_aton(address))[0]
        mo_map[mo_id] = {
            "bi_id": mo_biid,
            "adm_dom": mo_adm_dom,
            "pool": pool,
            "address": address,
            "profile": profile,
        }
    out = defaultdict(list)
    n_partitions = len(config.clickhouse.cluster_topology.split(","))
    for row in coll.find():
        mo_id = row["managed_object"]
        key = mo_id % n_partitions
        if len(out[key]) > CHUNK:
            for p, data in out.items():
                if not data:
                    continue
                publish(b"\n".join(data), "ch.events", partition=p)
            out = defaultdict(list)
        if mo_id not in mo_map:
            continue
        ts: datetime.datetime = row["timestamp"].replace(microsecond=0)
        out[key].append(
            orjson.dumps(
                {
                    "date": ts.date().isoformat(),
                    "ts": ts.isoformat(sep=" "),
                    "start_ts": ts.isoformat(sep=" "),
                    "event_id": str(row["_id"]),
                    "event_class": EventClass.get_by_id(row["event_class"]).bi_id,
                    "source": row.get("source", "other"),
                    "raw_vars": row["raw_vars"],
                    "resolved_vars": row["resolved_vars"],
                    "vars": row["vars"],
                    "snmp_trap_oid": row["raw_vars"].get(SNMP_TRPAP_OID, ""),
                    "message": row["raw_vars"].get("message", ""),
                    "managed_object": mo_map[mo_id]["bi_id"],
                    "pool": mo_map[mo_id]["pool"],
                    "ip": mo_map[mo_id]["address"],
                    "profile": mo_map[mo_id]["profile"],
                    # "vendor":
                    # "platform":
                    # "version":
                    "administrative_domain": mo_map[mo_id]["adm_dom"],
                }
            )
        )
    for p, data in out.items():
        if not data:
            continue
        publish(b"\n".join(data), "ch.events", partition=p)
