# ----------------------------------------------------------------------
# Test .get_by_id()
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from builtins import str
import pytest
import bson

# NOC modules
from .util import get_models, get_documents


@pytest.mark.parametrize("model", [x for x in get_models() if hasattr(x, "get_by_id")])
def test_model_get_by_id(model, database):
    assert callable(model.get_by_id)
    r = model.objects.all()[:1]
    if r:
        r = r[0]
        record = model.get_by_id(r.pk)
        assert record
        assert record.pk == r.pk
    else:
        record = model.get_by_id(0)
        assert not record


@pytest.mark.parametrize("model", [x for x in get_documents() if hasattr(x, "get_by_id")])
def test_document_get_by_id(model, database):
    assert callable(model.get_by_id)
    r = model.objects.first()
    if r:
        record = model.get_by_id(r.pk)
        assert record
        assert record.pk == r.pk
        record = model.get_by_id(str(r.pk))
        assert record
        assert record.pk == r.pk
    else:
        record = model.get_by_id(bson.ObjectId())
        assert not record
        record = model.get_by_id("000000000000000000000000")
        assert not record
