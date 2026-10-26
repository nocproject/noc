# ----------------------------------------------------------------------
# Test snmp_metrics directory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import orjson
import pytest

# NOC modules
from noc.config import config


def get_json_paths():
    """
    Get all JSON paths from snmp_metrics
    :return:
    """
    r = []
    metrics_dirs = []
    profiles_root = config.noc_base / "sa" / "profiles"
    for root, dirs, files in os.walk(str(profiles_root)):
        if "snmp_metrics" in dirs:
            metrics_dirs += [os.path.join(root, "snmp_metrics")]
    for root in metrics_dirs:
        for f in os.listdir(root):
            if f.endswith(".json"):
                r += [os.path.join(root, f)]
    return r


@pytest.mark.parametrize("path", get_json_paths())
def test_snmp_metrics_json(path) -> None:
    # Test loading
    try:
        with open(path) as f:
            data = orjson.loads(f.read())
    except ValueError as e:
        pytest.fail(f"Invalid JSON: {e}")
    assert isinstance(data, dict), "Must be dict"
