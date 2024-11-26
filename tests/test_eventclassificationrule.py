# ----------------------------------------------------------------------
# EventClassificationRule test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import datetime

# Third-party modules
import pytest
import orjson
from fs import open_fs

# NOC modules
from noc.services.classifier.ruleset import RuleSet
from noc.core.fm.event import Event
from noc.fm.models.mib import MIB
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.fm.models.eventclass import EventClass
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.config import config


COLLECTION_NAME = "test.events"
DEFAULT_EVENT_CLASS = "Unknown | Default"
DEFAULT_PROFILE = "Generic.Host"
MO_ADDRESS = "127.0.0.1"
MO_NAME = "test"
MO_ID = 1


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


def iter_test_rules():
    from noc.core.mongo.connection import connect

    connect()

    for e_rule in EventClassificationRule.objects.filter(test_cases__exists=True):
        yield e_rule


@pytest.fixture(
    scope="module",
    params=list(iter_test_rules()),
    ids=operator.attrgetter("name"),
)
def rule_case(database, request):
    return request.param


def test_rules_collection_cases(ruleset, rule_case):
    for e, v in rule_case.iter_cases():
        rule, e_vars = ruleset.find_rule(e, v)
        assert rule is not None, "Cannot find matching rule"
        assert rule.event_class == rule_case.event_class, "Mismatched event class %s vs %s" % (
            rule.event_class.name,
            rule_case.event_class.name,
        )
