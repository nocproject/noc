# ----------------------------------------------------------------------
# Reporter testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import os
import yaml

# NOC modules
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import ReportConfig, RunParams, OutputType
from noc.core.mongo.connection import connect


@pytest.mark.parametrize("report", ["report_simple_csv", "report_id_cache_poison"])
def test_report(report):
    path = os.path.realpath(os.path.dirname(__file__))
    with open(os.path.join(path, f"{report}.yml"), "rb") as f:
        cfg = yaml.safe_load(f)
    # r = yaml.safe_load(report_config)
    report_engine = ReportEngine(report_print_error=True)
    rp = RunParams(report=ReportConfig(**cfg), output_type=OutputType.CSV)
    connect()
    out_doc = report_engine.run_report(r_params=rp)
    re_out = out_doc.content.decode("utf8")
    re_out = re_out.replace("\r\n", "\n")
    with open(os.path.join(path, f"{report}.csv"), "r") as f:
        assert re_out == f.read()
