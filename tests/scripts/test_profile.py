# ----------------------------------------------------------------------
# SA Profile test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import pytest

# NOC modules
from noc.core.profile.loader import loader
from noc.core.profile.base import BaseProfile


def get_profiles():
    if os.environ.get("NOC_TEST_PROFILE"):
        p_name = os.environ["NOC_TEST_PROFILE"]
        return [x for x in loader.iter_profiles() if x == p_name]
    else:
        return list(loader.iter_profiles())


@pytest.fixture(scope="session", params=get_profiles())
def sa_profile(request):
    return request.param


@pytest.mark.dependency(name="iter_profiles")
def test_iter_profiles():
    assert len(list(loader.iter_profiles())) > 0


@pytest.mark.dependency(name="profile_loading", depends=["iter_profiles"])
def test_profile_loading(sa_profile):
    profile = loader.get_profile(sa_profile)
    assert profile is not None


@pytest.mark.dependency(depends=["profile_loading"])
def test_profile_type(sa_profile):
    profile = loader.get_profile(sa_profile)
    assert issubclass(profile, BaseProfile)


@pytest.mark.dependency(depends=["profile_loading"])
def test_profile_name(sa_profile):
    profile = loader.get_profile(sa_profile)
    assert getattr(profile, "name"), "Profile should has name"
    parts = profile.__module__.split(".")
    assert parts[-1] == "profile", "Profile must be in profile.py"
    if parts[-4:] == ["sa", "profiles", "Generic", "profile"]:
        pytest.skip("Generic profile")
    name = f"{parts[-3]}.{parts[-2]}"
    assert profile.name == name
