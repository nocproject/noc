# ----------------------------------------------------------------------
# Test zeroconf config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.services.zeroconf.models.zk import ZkConfig

ZK = """{
  "$version": "1",
  "$type": "zeroconf",
  "config": {
    "zeroconf": {
      "id": 12345,
      "key": "COFQI6Q3C23L5KUJKHYXEEBFEAOQJCUN",
      "interval": 300
    },
    "metrics": null
  },
  "collectors": [
    {
      "id": "dns_google",
      "type": "dns",
      "service": 1,
      "labels": ["test"],
      "interval": 10,
      "query": "google.com",
      "query_type": "A",
      "n": 5
    },
    {
      "id": "TWAMP G.711 Test",
      "type": "twamp_sender",
      "service": 2,
      "labels": ["dc1", "city1"],
      "interval": 10,
      "server": "127.0.0.1",
      "port": 862,
      "dscp": "ef",
      "n_packets": 250,
      "model": "g711",
      "test_timeout": 3.0
    }
  ]
}"""


def test_deserialize():
    data = orjson.loads(ZK)
    cfg = ZkConfig(**data)
    assert cfg.type == "zeroconf"
    assert cfg.version == "1"
    assert cfg.config.zeroconf.interval == 300
    assert len(cfg.collectors) == 2
    out = orjson.loads(cfg.model_dump_json(by_alias=True))
    assert data == out
