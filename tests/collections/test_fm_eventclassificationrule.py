# ----------------------------------------------------------------------
# EventClassificationRule test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import pytest
import orjson
from fs import open_fs

# NOC modules
from noc.services.classifier.ruleset import RuleSet
from noc.services.classifier.eventconfig import EventConfig
from noc.core.fm.event import Event
from noc.fm.models.mib import MIB
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.config import config
from .utils import CollectionTestHelper

helper = CollectionTestHelper(EventClassificationRule)
COLLECTION_NAME = "test.events"
DEFAULT_EVENT_CLASS = "Unknown | Default"
DEFAULT_PROFILE = "Generic.Host"
MO_ADDRESS = "127.0.0.1"
MO_NAME = "test"
MO_ID = 1


def teardown_module(module=None):
    """
    Reset all helper caches when leaving module
    :param module:
    :return:
    """
    helper.teardown()


@pytest.fixture(scope="module", params=helper.get_fixture_params(), ids=helper.fixture_id)
def event_class_rule(request):
    yield helper.get_object(request.param)


def iter_json_loader(urls):
    """
    Iterate over collections and return list of (path, data) pairs
    :param urls: List of pyfilesystem URLs
    :return:
    """
    if not urls:
        urls = []
    for url in urls:
        with open_fs(url) as fs:
            for path in fs.walk.files(filter=["*.json"]):
                with fs.open(path) as f:
                    data = orjson.loads(f.read())
                if not isinstance(data, list):
                    data = [data]
                for i in data:
                    yield path, i


@pytest.fixture(scope="module")
def ruleset():
    ruleset = RuleSet()
    ruleset.load()
    return ruleset


@pytest.fixture(params=list(iter_json_loader(config.tests.events_paths)))
def event(request):
    path, cfg = request.param
    coll = cfg.get("$collection", COLLECTION_NAME)
    assert coll == COLLECTION_NAME, "Invalid collection %s" % coll
    ec = EventClass.get_by_name(cfg.get("eventclass__name", DEFAULT_EVENT_CLASS))
    mo = ManagedObject(
        id=MO_ID,
        name=MO_NAME,
        address=MO_ADDRESS,
        profile=Profile.get_by_name(cfg.get("profile__name", DEFAULT_PROFILE)),
    )
    now = datetime.datetime.now()
    data = cfg.get("data", [])
    source = data.pop("source", "other")
    event = Event(
        ts=now.timestamp(),
        # start_timestamp=now,
        ta=mo,
        source=source,
        data=data,
    )
    request.fixturename = "events-%s" % cfg.get("uuid")
    # request.fspath = path
    return event, ec, cfg.get("vars", {})


def test_event(ruleset, event):
    e, expected_class, expected_vars = event
    e_vars = e.raw_vars.copy()
    if e.source == "SNMP Trap":
        e_vars.update(MIB.resolve_vars(e.raw_vars))
    rule, r_vars = ruleset.find_rule(e, e_vars)
    assert rule is not None, "Cannot find matching rule"
    assert rule.event_class == expected_class, "Mismatched event class %s vs %s" % (
        rule.event_class.name,
        expected_class.name,
    )
    ruleset.eval_vars(event, rule.event_class, e_vars)
    assert e_vars == expected_vars, "Mismatched vars"


# @pytest.fixture(
#     scope="module",
#     params=list(iter_test_rules()),
#     ids=operator.attrgetter("name"),
# )
# def rule_case(request):
#     return request.param


def test_rules_collection_cases(ruleset, event_class_rule):
    for e, v in event_class_rule.iter_cases():
        rule, e_vars = ruleset.find_rule(e, v)
        assert rule is not None, "Cannot find matching rule"
        assert rule.event_class_id == str(
            event_class_rule.event_class.id
        ), f"Mismatched event class '{rule.event_class_name}' vs '{event_class_rule.event_class.name}'"
        var_ctx = {"message": e.message}
        var_ctx |= v
        var_ctx |= e_vars
        for t in rule.vars_transform or []:
            t.transform(e_vars, var_ctx)
        if "ifindex" in e_vars and "interface_mock" in v:
            e_vars["interface"] = v.pop("interface_mock")
        elif "ifindex" in e_vars:
            assert "interface_mock" in e_vars, "interface_mock Required for ifindex transform test"
        cfg = EventConfig.from_config(
            EventClass.get_event_config(event_class_rule.event_class),
        )
        ruleset.eval_vars(e_vars, managed_object=None, e_cfg=cfg, by_test=True)
