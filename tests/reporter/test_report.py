# ----------------------------------------------------------------------
# Reporter testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import yaml

# Third-party modules
import pytest

# NOC modules
from noc.core.mongo.connection import connect
from noc.core.reporter.reportengine import ReportEngine
from noc.core.reporter.types import OutputType, ReportConfig, RunParams


@pytest.mark.parametrize(
    ("report", "params"),
    [
        ("report_simple_csv", {}),
        ("report_id_cache_poison", {}),
        ("report_object_summary_profile", {"report_type": "profile"}),
    ],
)
def test_report(report: str, params) -> None:
    path = os.path.realpath(os.path.dirname(__file__))
    with open(os.path.join(path, f"{report}.yml"), "rb") as f:
        cfg = yaml.safe_load(f)
    # r = yaml.safe_load(report_config)
    report_engine = ReportEngine(report_print_error=True)
    rp = RunParams(report_config=ReportConfig(**cfg), output_type=OutputType.CSV, params=params)
    connect()
    out_doc = report_engine.run_report(r_params=rp)
    re_out = out_doc.content.decode("utf8")
    re_out = re_out.replace("\r\n", "\n")
    with open(os.path.join(path, f"{report}.csv")) as f:
        assert re_out == f.read()
