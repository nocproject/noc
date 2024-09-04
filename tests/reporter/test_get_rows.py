# ----------------------------------------------------------------------
# Reporter testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import orjson
import polars as pl
from polars.testing import assert_frame_equal

# NOC modules
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import ReportQuery

query1 = ReportQuery(name="query1")
query1.json_data = (
    "["
    '{"id": 1, "name": "entity1"},'
    '{"id": 2, "name": "entity2"},'
    '{"id": 3, "name": "entity3"}'
    "]"
)

query_empty = ReportQuery(name="query_empty")
query_empty.json_data = "null"


def dataframe_from(query):
    return pl.DataFrame(orjson.loads(query.json_data))


@pytest.mark.parametrize(
    "queries, expected",
    [
        ([], None),
        ([query1], dataframe_from(query1)),
        ([query_empty], dataframe_from(query_empty)),
        ([query_empty, query1], dataframe_from(query_empty)),
        ([query1, query_empty], dataframe_from(query1)),
    ],
)
def test_get_rows(queries, expected):
    report_engine = ReportEngine()
    res = report_engine.get_dataset(queries, {}, []) or None
    if res is None:
        assert expected is None
    elif isinstance(res[0].data, pl.DataFrame):
        if isinstance(expected, pl.DataFrame):
            assert_frame_equal(res[0].data, expected)
        else:
            assert False
    else:
        assert False
