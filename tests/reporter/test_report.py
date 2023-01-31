# ----------------------------------------------------------------------
# Reporter testing
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
import yaml
import polars as pl
from io import BytesIO

# NOC modules
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import Report, RunParams, Template, ReportBand, OutputType
from noc.core.mongo.connection import connect

report1 = """
name: report
templates:
  DEFAULT:
    code: DEFAULT
    output_type: table
root_band:
  name: Root
  queries:
    - name: duplicate
      datasource: discoveryidcachepoisonds
  children:
    - name: header
    - name: master_data
      orientation: H
      queries:
        - name: q1
          query: parent.groupby(by="mac").agg(pl.first('reason'))
      children:
        name: duplicate_detail
        orientation: H
        queries:
          - name: detail
            query: parent.filter(pl.col('max') == {{ ctx['mac'] }})
"""

report2 = """
name: report
templates:
  DEFAULT:
    code: DEFAULT
    output_type: table
root_band:
    name: Root
    children:
      - name: header
      - name: master_data
        orientation: H
        queries:
          - name: master_data
            json: '[
            {
                "administrativedomain": "(006005)",
                "profile": "Huawei.VRP",
                "value": 1
            },
            {
                "administrativedomain": "(084088)",
                "profile": "Generic.Host",
                "value": 2
            },
            {
                "administrativedomain": "(207029)",
                "profile": "Generic.Host",
                "value": 2
            }
        ]'

"""


def test_report():
    r = yaml.safe_load(report2)
    re = ReportEngine()
    rp = RunParams(report=Report(**r))
    out = BytesIO()
    connect()
    re.run_report(r_params=rp, out=out)
    out.seek(0)
    assert (
        out.read()
        == b"""administrativedomain;profile;value\n(006005);Huawei.VRP;1\n(084088);Generic.Host;2\n(207029);Generic.Host;2\n"""
    )
