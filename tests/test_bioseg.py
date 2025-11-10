# ----------------------------------------------------------------------
# BioSeg test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
import pytest
import bson

# NOC modules
from noc.core.bioseg.policies.loader import loader
from noc.core.bioseg.policies.base import BaseBioSegPolicy
from noc.core.bioseg.policies.keep import KeepBioSegPolicy
from noc.core.bioseg.policies.merge import MergeBioSegPolicy
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile, BioCollisionPolicy
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile

# ns_id1 < ns_id2
ns_id1 = bson.ObjectId("5f2a62bce9d7278f02ed1230")
ns_id2 = bson.ObjectId("5f2a62c0e9d7278f02ed1231")


def patch_model(model):
    def save():
        pass

    def _reset_caches():
        pass

    model.save = save
    model._reset_caches = _reset_caches
    return model


class MockBioSegPolicy(BaseBioSegPolicy):
    N = 10
    LEVEL = 10
    _objects = []

    def get_objects(self, seg: NetworkSegment) -> List[ManagedObject]:
        if not self._objects:
            profile = ManagedObjectProfile(name="mock", level=self.LEVEL)
            self._objects = [
                patch_model(
                    ManagedObject(name="%d" % (i + 1), segment=self.target, object_profile=profile)
                )
                for i in range(self.N)
            ]

        objects = [mo for mo in self._objects if mo.segment == seg]
        self.set_power(seg, sum(mo.object_profile.level for mo in objects))
        return objects


@pytest.mark.parametrize("name", ["keep", "eat", "feed", "merge", "calcify"])
def test_loader(name):
    policy_cls = loader.get_class(name)
    assert policy_cls
    assert policy_cls.name == name


def test_set_power():
    attacker = NetworkSegment(id=ns_id1, name="attacker")
    target = NetworkSegment(id=ns_id2, name="target")
    policy = BaseBioSegPolicy(attacker, target)
    assert not policy._powers
    policy.set_power(attacker, 10)
    assert policy.get_power(attacker) == 10
    policy.set_power(target, 20)
    assert policy.get_power(target) == 20
    policy.set_power(attacker, 30)
    assert policy.get_power(attacker) == 30


def test_consume_objects():
    profile = NetworkSegmentProfile(name="mock", is_persistent=False)
    attacker = NetworkSegment(id=ns_id1, name="attacker", profile=profile)
    target = NetworkSegment(id=ns_id2, name="target", profile=profile)
    policy = MockBioSegPolicy(attacker, target)
    assert len(policy.get_objects(attacker)) == 0
    assert len(policy.get_objects(target)) == policy.N
    policy.consume_objects(target, attacker)
    assert len(policy.get_objects(attacker)) == policy.N
    assert len(policy.get_objects(target)) == 0
    assert policy.get_power(attacker) == policy.N * policy.LEVEL
    assert policy.get_power(target) == 0


def test_base_trial():
    attacker = NetworkSegment(name="attacker")
    target = NetworkSegment(name="target")
    policy = BaseBioSegPolicy(attacker, target)
    with pytest.raises(NotImplementedError):
        policy.trial()


def test_keep_trial():
    attacker = NetworkSegment(name="attacker")
    target = NetworkSegment(name="target")
    policy = KeepBioSegPolicy(attacker, target)
    assert policy.trial() == "keep"


@pytest.mark.parametrize(
    ("a_power", "a_id", "t_power", "t_id", "expected"),
    [
        (20, ns_id1, 10, ns_id2, "eat"),
        (10, ns_id1, 20, ns_id2, "feed"),
        (30, ns_id1, 30, ns_id2, "eat"),
        (30, ns_id2, 30, ns_id1, "feed"),
    ],
)
def test_merge_policy(a_power, a_id, t_power, t_id, expected):
    """
    Test MERGE rule
    :return:
    """
    # Mock segments
    attacker = NetworkSegment(id=a_id, name="attacker")
    target = NetworkSegment(id=t_id, name="target")
    policy = MergeBioSegPolicy(attacker, target)
    # Mock powers
    policy.set_power(attacker, a_power)
    policy.set_power(target, t_power)
    effective_policy = policy.get_effective_policy()
    assert effective_policy
    assert effective_policy.name == expected


@pytest.mark.parametrize(
    ("match_type", "is_persistent", "outcome"),
    [
        ("*", False, True),
        ("*", True, True),
        ("p", False, False),
        ("p", True, True),
        ("f", False, True),
        ("f", True, False),
    ],
)
def test_collision_policy_type(match_type, is_persistent, outcome):
    cp = BioCollisionPolicy(match_type=match_type)
    assert cp.check_type(is_persistent) is outcome


@pytest.mark.parametrize(
    ("match_level", "attacker_level", "target_level", "outcome"),
    [
        # match -
        ("-", 10, 10, False),
        ("-", 10, None, False),
        ("-", None, 10, False),
        ("-", None, None, True),
        # match *
        ("*", None, None, False),
        ("*", 10, None, False),
        ("*", None, 10, False),
        ("*", 10, 10, True),
        # match <
        ("<", 10, 1, False),
        ("<", 10, 10, False),
        ("<", 10, 20, True),
        # match <=
        ("<=", 10, 1, False),
        ("<=", 10, 10, True),
        ("<=", 10, 20, True),
        # match ==
        ("==", 10, 1, False),
        ("==", 10, 10, True),
        ("==", 10, 20, False),
        # match >=
        (">=", 10, 1, True),
        (">=", 10, 10, True),
        (">=", 10, 20, False),
        # match >
        (">", 10, 1, True),
        (">", 10, 10, False),
        (">", 10, 20, False),
    ],
)
def test_collision_policy_level(match_level, attacker_level, target_level, outcome):
    cp = BioCollisionPolicy(match_type="*", match_level=match_level)
    assert cp.check_level(attacker_level, target_level) is outcome


@pytest.mark.parametrize(
    ("attacker_policy", "target_policy", "expected"),
    [
        # Merge
        ("merge", "merge", "feed"),
        ("merge", "keep", "keep"),
        ("merge", "eat", "feed"),
        ("merge", "feed", "keep"),
        ("merge", "calcify", "keep"),
        # Keep
        ("keep", "merge", "keep"),
        ("keep", "keep", "keep"),
        ("keep", "eat", "feed"),
        ("keep", "feed", "keep"),
        ("keep", "calcify", "keep"),
        # Eat
        ("eat", "merge", "keep"),
        ("eat", "keep", "keep"),
        ("eat", "eat", "keep"),
        ("eat", "feed", "keep"),
        ("eat", "calcify", "keep"),
        # Feed
        ("feed", "merge", "feed"),
        ("feed", "keep", "keep"),
        ("feed", "eat", "feed"),
        ("feed", "feed", "keep"),
        ("feed", "calcify", "keep"),
        # Calcify
        ("calcify", "merge", "calcify"),
        ("calcify", "keep", "calcify"),
        ("calcify", "eat", "calcify"),
        ("calcify", "feed", "calcify"),
        ("calcify", "calcify", "calcify"),
    ],
)
def test_collision_persist(attacker_policy, target_policy, expected):
    policy = loader.get_class(target_policy)
    profile = NetworkSegmentProfile(name="stub", is_persistent=True)
    target = NetworkSegment(name="target", profile=profile)
    result = policy.get_effective_policy_name(target, attacker_policy)
    assert result == expected
    assert loader.get_class(result)


@pytest.mark.parametrize(
    ("attacker_policy", "target_policy", "expected"),
    [
        # Merge
        ("merge", "merge", "merge"),
        ("merge", "keep", "keep"),
        ("merge", "eat", "feed"),
        ("merge", "feed", "eat"),
        ("merge", "calcify", "keep"),
        # Keep
        ("keep", "merge", "keep"),
        ("keep", "keep", "keep"),
        ("keep", "eat", "feed"),
        ("keep", "feed", "keep"),
        ("keep", "calcify", "keep"),
        # Eat
        ("eat", "merge", "eat"),
        ("eat", "keep", "eat"),
        ("eat", "eat", "merge"),
        ("eat", "feed", "eat"),
        ("eat", "calcify", "keep"),
        # Feed
        ("feed", "merge", "feed"),
        ("feed", "keep", "feed"),
        ("feed", "eat", "feed"),
        ("feed", "feed", "merge"),
        ("feed", "calcify", "feed"),
        # Calcify
        ("calcify", "merge", "calcify"),
        ("calcify", "keep", "calcify"),
        ("calcify", "eat", "feed"),
        ("calcify", "feed", "eat"),
        ("calcify", "calcify", "calcify"),
    ],
)
def test_collision_floating(attacker_policy, target_policy, expected):
    policy = loader.get_class(target_policy)
    profile = NetworkSegmentProfile(name="stub", is_persistent=False)
    target = NetworkSegment(name="target", profile=profile)
    result = policy.get_effective_policy_name(target, attacker_policy)
    assert result == expected
    assert loader.get_class(result)
