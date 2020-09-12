# ----------------------------------------------------------------------
# Test snmp_metrics directory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import pytest
import orjson


def get_json_paths():
    """
    Get all JSON paths from snmp_metrics
    :return:
    """
    r = []
    metrics_dirs = []
    for root, dirs, files in os.walk(os.path.join("sa", "profiles")):
        if "snmp_metrics" in dirs:
            metrics_dirs += [os.path.join(root, "snmp_metrics")]
    for root in metrics_dirs:
        for f in os.listdir(root):
            if f.endswith(".json"):
                r += [os.path.join(root, f)]
    return r


@pytest.mark.parametrize("path", get_json_paths())
def test_snmp_metrics_json(path):
    # Test loading
    try:
        with open(path) as f:
            data = orjson.loads(f.read())
    except ValueError as e:
        pytest.fail("Invalid JSON: %s" % e)
    assert isinstance(data, dict), "Must be dict"
