# ----------------------------------------------------------------------
# Test collections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path
from typing import Iterable

# Third-party modules
import pytest
import orjson


def iter_path() -> Iterable[Path]:
    root = Path("collections")
    exclude = {Path("collections", "package.json")}
    for fn in root.rglob("*.json"):
        if fn not in exclude:
            yield fn


@pytest.mark.parametrize("path", list(iter_path()), ids=str)
def test_json(path: Path) -> None:
    with open(path) as fp:
        data = orjson.loads(fp.read())
    # @todo: Replace with assert
    if "$collection" not in data:
        # pytest.xfail("$collection is missed")
        return
    assert path.parts[1] == data["$collection"]
