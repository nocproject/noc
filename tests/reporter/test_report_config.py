# ----------------------------------------------------------------------
# Datasource testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import os
import yaml
from io import BytesIO

# NOC modules
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import ReportConfig, RunParams, OutputType
from noc.core.mongo.connection import connect
from noc.services.web.base.site import site


class RequestStub(object):
    def __init__(self, user):
        self.user = user


@pytest.mark.parametrize("report", ["report_objectsummary"])  #  "report_datasource_cmp"
def test_report_config(report):
    path = os.path.realpath(os.path.dirname(__file__))
    with open(os.path.join(path, f"{report}.yml"), "rb") as f:
        cfg = yaml.safe_load(f)
    r_cfg = ReportConfig(**cfg)
    report_engine = ReportEngine()
    rp = RunParams(report=r_cfg)
    out = BytesIO()
    connect()
    report_engine.run_report(r_params=rp, out=out)
    out.seek(0)
    site.autodiscover()
    app = site.apps[r_cfg.name]
    args = {}
    request = RequestStub(None)
    report = app.get_data()
    if r_cfg.templates["DEFAULT"].output_type == OutputType.HTML:
        assert out.read().decode("utf8") == report.to_html()
    else:
        assert out.read().decode("utf8") == report.to_csv()
