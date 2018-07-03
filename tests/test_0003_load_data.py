# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Load initial data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from fs import open_fs
import ujson
# NOC modules
from noc.config import config
from noc.models import get_model


def iter_data():
    for url in config.tests.fixtures_paths:
        with open_fs(url) as fs:
            for path in fs.walk.files(filter=["*.json"]):
                with fs.open(path) as f:
                    data = ujson.loads(f.read())
                if not isinstance(data, list):
                    data = [data]
                for i in data:
                    yield path, i


def get_data_name(v):
    return "%s|%s|%s" % (v[0], v[1]["$model"], v[1]["id"])


@pytest.fixture(params=list(iter_data()), ids=get_data_name)
def initial_data(request):
    path, cfg = request.param
    return cfg


def test_load_data(initial_data):
    data = initial_data
    assert "$model" in data
    model = get_model(data["$model"])
    assert model
    kwargs = {}
    for k in data:
        if k.startswith("$"):
            continue
        kwargs[k] = data[k]
    d = model(**kwargs)
    d.save()
    assert d.pk
