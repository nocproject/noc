# ----------------------------------------------------------------------
# ManagedObjectCollector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.main.models.pool import Pool
from noc.wf.models.state import State
from .base import BaseCollector


class ManagedObjectCollector(BaseCollector):
    name = "managedobject"

    SQL_POOL_MO = """SELECT
      pool AS pool_id,
      state AS state_id,
      COUNT(*) AS pool_state_count,
      COUNT(*) FILTER (where diagnostics -> 'CLI' ->> 'state' = 'failed') as cli_f_count,
      COUNT(*) FILTER (where diagnostics -> 'CLI' ->> 'state' = 'enabled')  as cli_e_count,
      COUNT(*) FILTER (where diagnostics -> 'CLI' ->> 'state' = 'blocked')  as cli_b_count,
      COUNT(*) FILTER (where diagnostics -> 'SNMP' ->> 'state' = 'failed') as snmp_f_count,
      COUNT(*) FILTER (where diagnostics -> 'SNMP' ->> 'state' = 'enabled')  as snmp_e_count,
      COUNT(*) FILTER (where diagnostics -> 'SNMP' ->> 'state' = 'blocked')  as snmp_b_count
    FROM sa_managedobject
    GROUP BY pool, state
    """

    def iter_metrics(self):
        pool_stat = defaultdict(list)
        diag_state = defaultdict()
        for (
            pool_id,
            state_id,
            count,
            cli_f_count,
            cli_e_count,
            cli_b_count,
            snmp_f_count,
            snmp_e_count,
            snmp_b_count,
        ) in self.pg_execute(self.SQL_POOL_MO):
            pool = Pool.get_by_id(pool_id)
            state = State.get_by_id(state_id)
            if not pool or not state:
                continue
            pool_stat[pool.name].append(count)
            if state.name == "Managed":
                diag_state[pool.name] = {
                    "cli_enabled": cli_e_count,
                    "cli_failed": cli_f_count,
                    "cli_blocked": cli_b_count,
                    "snmp_failed": snmp_f_count,
                    "snmp_enabled": snmp_e_count,
                    "snmp_blocked": snmp_b_count,
                }
            yield (
                "inventory_managedobject_count",
                ("pool", pool.name),
                ("state", state.name),
            ), count
        for pool_name, count in pool_stat.items():
            yield ("inventory_managedobject_total", ("pool", pool_name)), sum(count)
            if pool_name not in diag_state:
                continue
            # Set diagnostic state metrics
            data = diag_state[pool_name]
            yield (
                (
                    "diag_managedobject_count",
                    ("pool", pool_name),
                    ("type", "cli"),
                    ("state", "Enabled"),
                ),
                data["cli_enabled"],
            )
            yield (
                (
                    "diag_managedobject_count",
                    ("pool", pool_name),
                    ("type", "cli"),
                    ("state", "Failed"),
                ),
                data["cli_failed"],
            )
            yield (
                (
                    "diag_managedobject_count",
                    ("pool", pool_name),
                    ("type", "cli"),
                    ("state", "Blocked"),
                ),
                data["cli_blocked"],
            )
            yield (
                (
                    "diag_managedobject_count",
                    ("pool", pool_name),
                    ("type", "snmp"),
                    ("state", "Enabled"),
                ),
                data["snmp_enabled"],
            )
            yield (
                (
                    "diag_managedobject_count",
                    ("pool", pool_name),
                    ("type", "snmp"),
                    ("state", "Failed"),
                ),
                data["snmp_failed"],
            )
            yield (
                (
                    "diag_managedobject_count",
                    ("pool", pool_name),
                    ("type", "snmp"),
                    ("state", "Blocked"),
                ),
                data["snmp_blocked"],
            )
