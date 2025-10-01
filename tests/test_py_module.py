# ---------------------------------------------------------------------
# Test python module loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import ast
from typing import Iterable, List
from pathlib import Path

# Third-party modules
import pytest
import cachetools


_ALLOW_XFAIL = {
    "noc.services.login.backends.pam",
    "noc.services.web.apps.kb.parsers.mediawiki",
    "noc.services.classifier.xrulelookup",
    "noc.commands.translation",
    "noc.gis.tile",
    "noc.core.etl.extractor.vcenter",
    "noc.core.etl.extractor.zabbix",
}


def _allow_xfail(module: str) -> bool:
    """
    Allow module to be xfail due to import errors
    :param module: Module name
    :return:
    """
    return module in _ALLOW_XFAIL or module.startswith("noc.sa.profiles.VMWare")


@cachetools.cached(cache={})
def get_files() -> List[Path]:
    """Get list of all python files in src/noc."""
    r: List[Path] = []
    for root, _, files in os.walk(Path("src", "noc"), followlinks=True):
        for f in files:
            if not f.startswith(".") and f.endswith(".py"):
                r.append(Path(root) / f)
    return r


INIT_PY = "__init__.py"


def iter_py_modules() -> Iterable[str]:
    """Iterate over module names."""
    root = Path("src")
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


@pytest.mark.parametrize("module", iter_py_modules())
def test_import(module: str) -> None:
    try:
        m = __import__(module, {}, {}, "*")
        assert m
    except (ImportError, ModuleNotFoundError, NotImplementedError) as e:
        if _allow_xfail(module):
            pytest.xfail(str(e))
        else:
            pytest.fail(str(e))


@pytest.mark.parametrize("path", iter_init())
def test_init(path: Path) -> None:
    with open(path) as f:
        data = f.read()
    if "TESTS: ALLOW_NON_EMPTY_INIT" in data:
        return  # exclusion
    n = compile(data, path, "exec", ast.PyCF_ONLY_AST)
    assert bool(n.body) or not bool(data), "__init__.py must be empty"
