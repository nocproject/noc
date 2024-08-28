# ---------------------------------------------------------------------
# Test sa scripts
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import pytest

# NOC modules
from noc.core.script.loader import loader
from noc.core.interface.base import BaseInterface
from noc.core.script.base import BaseScript

IGNORED_VENDOR = ["VMWare"]


def get_scripts():
    if os.environ.get("NOC_TEST_SCRIPT"):
        s_name = os.environ["NOC_TEST_SCRIPT"]
        return [x for x in loader.iter_scripts() if x == s_name]
    elif os.environ.get("NOC_TEST_PROFILE"):
        p_name = "%s." % os.environ["NOC_TEST_PROFILE"]
        return [x for x in loader.iter_scripts() if x.startswith(p_name)]
    else:
        return [x for x in loader.iter_scripts() if x.split(".")[0] not in IGNORED_VENDOR]


@pytest.fixture(scope="session", params=get_scripts())
def sa_script(request):
    return request.param


@pytest.mark.dependency(name="iter_scripts")
def test_iter_scripts():
    assert len(list(loader.iter_scripts())) > 0


@pytest.mark.dependency(name="script_loading", depends=["iter_scripts"])
def test_script_loading(sa_script):
    script = loader.get_script(sa_script)
    assert script is not None


@pytest.mark.dependency(depends=["script_loading"])
def test_script_type(sa_script):
    script = loader.get_script(sa_script)
    assert issubclass(script, BaseScript)


@pytest.mark.dependency(depends=["script_loading"])
def test_script_name(sa_script):
    script = loader.get_script(sa_script)
    assert getattr(script, "name"), "Script should has name"
    req_name = script.__module__
    if req_name.startswith("noc.sa.profiles."):
        req_name = req_name[16:]
    assert script.name == req_name


@pytest.mark.dependency(depends=["script_loading"])
def test_script_interface(sa_script):
    script = loader.get_script(sa_script)
    assert getattr(script, "interface", None) is not None, "Script should has 'interface' attribute"
    assert issubclass(script.interface, BaseInterface)
