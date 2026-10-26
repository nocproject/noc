# ----------------------------------------------------------------------
# Datasource testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
from noc.services.web.base.site import site


class RequestStub:
    def __init__(self, user) -> None:
        self.user = user


@pytest.mark.parametrize("report", ["report_objectsummary", "report_source_classificationrule"])
def test_report_config(report: str) -> None:
    path = os.path.realpath(os.path.dirname(__file__))
    with open(os.path.join(path, f"{report}.yml"), "rb") as f:
        cfg = yaml.safe_load(f)
    args = cfg.pop("args", None) or {}
    if "request" in args:
        args["request"] = RequestStub(None)
    r_cfg = ReportConfig(**cfg)
    report_engine = ReportEngine(report_print_error=True)
    rp = RunParams(report_config=r_cfg, params=args)
    connect()
    out_doc = report_engine.run_report(r_params=rp)
    site.autodiscover()
    app = site.apps[r_cfg.name]
    report = app.get_data(**args)
    if r_cfg.templates["DEFAULT"].output_type == OutputType.HTML:
        assert out_doc.content.decode("utf8") == report.to_html(include_buttons=False)
    else:
        assert out_doc.content.decode("utf8") == report.to_csv()
