# ----------------------------------------------------------------------
# Exv backend test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
import pytest

# NOC modules
from noc.core.config.backends.env import EnvParams
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import IntParameter, StringParameter


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("env:///NOC", "NOC"),
        ("env:///NOC_CONFIG", "NOC_CONFIG"),
        ("env://localhost/NOC", "NOC"),
        ("env:////NOC", "NOC"),
        ("env:///", ""),
        ("env://", ""),
    ],
)
def test_env_params_from_url(url: str, expected: str) -> None:
    params = EnvParams.from_url(url)
    assert params == EnvParams(prefix=expected)


def test_config() -> None:
    class Config(BaseConfig):
        x = IntParameter()

        class y(ConfigSection):
            z = StringParameter()
            a = StringParameter(default="x")

    pid = os.getpid()
    prefix = f"NOC_TEST_{pid}"
    ENV = [
        (f"{prefix}_X", "15"),
        (f"{prefix}_Y_Z", "s"),
        (f"{prefix}_Y_a", "y"),  # must be ignored
    ]

    for k, v in ENV:
        os.environ[k] = v
    try:
        config = Config()
        config.load(f"env:///{prefix}")
        assert config.x == 15
        assert config.y.z == "s"
        assert config.y.a == "x"
    finally:
        for k, _ in ENV:
            del os.environ[k]
