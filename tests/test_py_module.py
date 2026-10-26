# ---------------------------------------------------------------------
# Test python module loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import ast
import importlib
from collections.abc import Iterable
from pathlib import Path

# Third-party modules
import cachetools
import pytest

# NOC modules
from noc.config import config

# Transitonal only guard.
# Remove after step 8 of NEP-0101
assert config.noc_base.parts[-2:] == ("src", "noc"), f"Invalid {config.noc_base}"

_ALLOW_XFAIL = {
    "noc.services.login.backends.pam",
    "noc.services.web.apps.kb.parsers.mediawiki",
    "noc.commands.translation",
    "noc.gis.tile",
    "noc.core.etl.extractor.vcenter",
    "noc.core.etl.extractor.zabbix",
    "noc.services.metricscollector.paths.vmagent",
    "noc.services.metricscollector.models.vmagent",
}


def _allow_xfail(module: str) -> bool:
    """
    Allow module to be xfail due to import errors
    :param module: Module name
    :return:
    """
    return module in _ALLOW_XFAIL or module.startswith("noc.sa.profiles.VMWare")


@cachetools.cached(cache={})
def get_files() -> list[Path]:
    """Get list of all Python files in the NOC package."""
    return [
        path
        for path in config.noc_base.rglob("*.py", recurse_symlinks=True)
        if not path.name.startswith(".")
    ]


INIT_PY = "__init__.py"


def iter_py_modules() -> Iterable[str]:
    """Iterate over module names."""
    root = config.noc_base.parent
    for path in get_files():
        rel = path.relative_to(root)
        if path.name == INIT_PY:
            yield ".".join(rel.parts[:-1])
        else:
            yield ".".join(rel.with_suffix("").parts)


def iter_init() -> Iterable[Path]:
    """Iterate __init__.py paths."""
    for path in get_files():
        if path.name == INIT_PY:
            yield path


@pytest.mark.parametrize("module", list(iter_py_modules()))
def test_import(module: str) -> None:
    try:
        m = importlib.import_module(module)
        assert m
    except (ImportError, ModuleNotFoundError, NotImplementedError) as e:
        if _allow_xfail(module):
            pytest.xfail(str(e))
        else:
            pytest.fail(str(e))


@pytest.mark.parametrize("path", list(iter_init()))
def test_init(path: Path) -> None:
    data = path.read_text()
    if "TESTS: ALLOW_NON_EMPTY_INIT" in data:
        pytest.skip("allowed to be non-empty")
    n = compile(data, path, "exec", ast.PyCF_ONLY_AST)
    assert bool(n.body) or not bool(data), f"{path} must be empty"
