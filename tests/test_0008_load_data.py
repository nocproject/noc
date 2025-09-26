# ----------------------------------------------------------------------
# Load initial data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from fs import open_fs
import orjson
from django.db import models

# NOC modules
from noc.config import config
from noc.models import get_model, is_document
from noc.core.model.fields import DocumentReferenceField, CachedForeignKey


def iter_data():
    for url in config.tests.fixtures_paths:
        with open_fs(url) as fs:
            for path in sorted(fs.walk.files(filter=["*.json"])):
                with fs.open(path) as f:
                    data = orjson.loads(f.read())
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


model_refs = {}  # model -> name -> model
m2m_refs = {}  # model -> name -> model


def test_load_data(initial_data):
    global model_refs, m2m_refs

    data = initial_data
    assert "$model" in data
    model = get_model(data["$model"])
    assert model
    # Get reference fields
    refs = model_refs.get(data["$model"])  # name -> model
    mrefs = m2m_refs.get(data["$model"])  # name -> model
    if refs is None:
        refs = {}
        mrefs = {}
        if is_document(model):
            pass
        else:
            # Django models
            for f in model._meta.fields:
                if isinstance(f, (models.ForeignKey, CachedForeignKey)):
                    refs[f.name] = f.remote_field.model
                elif isinstance(f, DocumentReferenceField):
                    refs[f.name] = f.document
            for f in model._meta.many_to_many:
                if isinstance(f, models.ManyToManyField):
                    mrefs[f.name] = f.remote_field.model
        model_refs[data["$model"]] = refs
        m2m_refs[data["$model"]] = mrefs
    kwargs = {}
    m2m = {}
    for k in data:
        if k.startswith("$"):
            continue
        if k in refs:
            kwargs[k] = _dereference(refs[k], data[k])
        elif k in mrefs:
            m2m[k] = [_dereference(mrefs[k], x) for x in data[k]]
        else:
            kwargs[k] = data[k]
    d = model(**kwargs)
    d.save()
    assert d.pk
    # M2M fields
    for k in m2m:
        for r in m2m[k]:
            getattr(d, k).add(r)


def _dereference(model, id):
    if hasattr(model, "get_by_id"):
        return model.get_by_id(id)
    else:
        return model.objects.get(pk=id)
