# ----------------------------------------------------------------------
#  Lock Metric Proxy
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2024 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.pm.utils import MetricProxy
from noc.core.mongo.connection import connect

SQL_INTERFACE_LOAD_OUT = """
              SELECT interface, managed_object, argMax(load_out, ts) AS load_out
              FROM interface
              WHERE
              date >= %s
              AND ts >= %s
              AND (managed_object = 9016826725858827563)
              GROUP BY interface, managed_object
              FORMAT JSONEachRow
"""


def test_mp():
    connect()
    mp = MetricProxy(managed_object=9016826725858827563)
    qs = mp.interface(group_by=["interface", "managed_object"]).load_out
    assert qs.query_expr().strip() == SQL_INTERFACE_LOAD_OUT.strip()
    mp = MetricProxy(managed_object=9016826725858827563)
    qs = mp.interface(queries=["load_out"], group_by=["interface", "managed_object"])
    assert qs.query_expr().strip() == SQL_INTERFACE_LOAD_OUT.strip()
