# ----------------------------------------------------------------------
# Consul backend test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.config.backends.base import BaseConfigBackend
from noc.core.config.backends.consul import DEFAULT_CONSUL_PORT, ConsulBackend, ConsulParams
from noc.core.config.base import BaseConfig, ConfigSection
from noc.core.config.params import IntParameter, StringParameter


class MockConsulBackend(ConsulBackend):
    async def get_kv(self) -> list[dict[str, object]] | None:
        return [
            {"Key": "noc/config/x", "Value": b"15"},
            {"Key": "noc/config/y/z", "Value": b"s"},
        ]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "consul://localhost/config",
            ConsulParams(
                host="localhost",
                port=DEFAULT_CONSUL_PORT,
                path="config",
            ),
        ),
        (
            "consul://consul.example.com:8600/noc/config",
            ConsulParams(
                host="consul.example.com",
                port=8600,
                path="noc/config",
            ),
        ),
        (
            "consul://127.0.0.1:8500/",
            ConsulParams(
                host="127.0.0.1",
                port=8500,
                path="",
            ),
        ),
    ],
)
def test_consul_params_from_url(url: str, expected: ConsulParams) -> None:
    params = ConsulParams.from_url(url)

    assert params == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "consul://localhost/config?token=secret",
            "secret",
        ),
        (
            "consul://localhost/config?token=my%20token",
            "my token",
        ),
        (
            "consul://localhost/config?foo=bar&token=secret",
            "secret",
        ),
        (
            "consul://localhost/config",
            None,
        ),
    ],
)
def test_consul_params_token(url: str, expected: str | None) -> None:
    params = ConsulParams.from_url(url)
    assert params.token == expected


def test_config() -> None:
    class Config(BaseConfig):
        x = IntParameter()

        class y(ConfigSection):
            z = StringParameter()
            a = StringParameter(default="x")

        @classmethod
        def get_backend(cls, url: str) -> BaseConfigBackend:
            assert url.startswith("consul://")
            return MockConsulBackend(url)

    config = Config()
    config.load("consul://127.0.0.1:8500/noc/config?token=123")
    assert config.x == 15
    assert config.y.z == "s"
    assert config.y.a == "x"
