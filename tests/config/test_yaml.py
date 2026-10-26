# ----------------------------------------------------------------------
# YAML backend test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import tempfile
from pathlib import Path

# Third-party modules
import pytest

# NOC modules
from noc.core.config.backends.yaml import YAMLParams
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import IntParameter, StringParameter

YAML = """x: "15"
y:
    z: "s"
"""


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("yaml:///etc/noc/config.yml", Path("/etc/noc/config.yml")),
        ("yaml:///tmp/config.yaml", Path("/tmp/config.yaml")),
        ("yaml:///", Path("/")),
    ],
)
def test_yaml_params_from_url(url: str, expected: Path) -> None:
    params = YAMLParams.from_url(url)
    assert params == YAMLParams(path=expected)


def test_config() -> None:
    class Config(BaseConfig):
        x = IntParameter()

        class y(ConfigSection):
            z = StringParameter()
            a = StringParameter(default="x")

    config = Config()
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp:
        p = Path(tmp.name)
        p.write_text(YAML)
        config.load(f"yaml://{tmp.name}")
        assert config.x == 15
        assert config.y.z == "s"
        assert config.y.a == "x"
