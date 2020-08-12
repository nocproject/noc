# ----------------------------------------------------------------------
# Test sa.profilecheckrules collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict

# Third-party modules
import pytest

# NOC modules
from noc.sa.models.profilecheckrule import ProfileCheckRule
from .utils import CollectionTestHelper
from noc.core.validators import is_oid
from noc.core.mib import mib


class PCRHelper(CollectionTestHelper):
    def __init__(self, model):
        super().__init__(model)
        self._oid_count = defaultdict(int)

    def get_object(self, path):
        obj = super().get_object(path)
        if obj.method == "snmp_v2c_get" and obj.match_method == "eq":
            self._oid_count[obj.method, mib[obj.param], obj.match_method, obj.value] += 1
        return obj

    def get_oid_count(self, param, value):
        return self._oid_count[param, value]


helper = PCRHelper(ProfileCheckRule)


def teardown_module(module=None):
    """
    Reset all helper caches when leaving module
    :param module:
    :return:
    """
    helper.teardown()


@pytest.fixture(scope="module", params=helper.get_fixture_params(), ids=helper.fixture_id)
def model(request):
    yield helper.get_object(request.param)


@pytest.mark.xfail
def test_uuid_unique(model):
    assert helper.get_uuid_count(model.uuid) == 1, "UUID %s is not unique" % model.uuid


def test_name_unique(model):
    assert helper.get_name_count(model.name) == 1, "Name '%s' is not unique" % model.name


rx_mib = re.compile(r"^[0-9a-z][0-9a-z\-_]::[0-9a-z][0-9a-z\-_]*(\.\d+)*$", re.IGNORECASE)


def test_oid(model):
    def check_oid(oid):
        if oid == "0.0":
            # For ISKRATEL VDSL-2 sysObjectID ProfileCheckRule
            return True
        if is_oid(oid):
            return True
        if "::" not in oid:
            return False
        return rx_mib.match(oid) is not None

    if model.method != "snmp_v2c_get":
        pytest.skip("Not relevant")
    assert check_oid(mib[model.param]), "Invalid OID: '%s'" % model.param
    if model.match_method != "eq":
        pytest.skip("Not relevant")
    assert check_oid(model.value)


def test_oid_unique(model):
    if model.method != "snmp_v2c_get" or model.match_method != "eq":
        pytest.skip("Not relevant")
    assert (
        helper.get_oid_count(mib[model.param], model.value) == 0
    ), "'%s' == '%s' is not unique" % (model.param, model.value)
