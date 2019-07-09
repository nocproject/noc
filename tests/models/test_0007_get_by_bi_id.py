# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test .get_by_bi_id()
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import pytest

# NOC modules
from .util import get_models, get_documents


@pytest.mark.parametrize("model", [x for x in get_models() if hasattr(x, "get_by_bi_id")])
def test_model_get_by_bi_id(model):
    assert callable(model.get_by_bi_id)
    r = model.objects.all()[:1]
    if r:
        r = r[0]
        record = model.get_by_bi_id(r.bi_id)
        assert record
        assert record.bi_id == r.bi_id
    else:
        record = model.get_by_bi_id(0)
        assert not record


@pytest.mark.parametrize("model", [x for x in get_documents() if hasattr(x, "get_by_bi_id")])
def test_document_get_by_bi_id(model):
    assert callable(model.get_by_bi_id)
    r = model.objects.first()
    if r:
        record = model.get_by_bi_id(r.bi_id)
        assert record
        assert record.bi_id == r.bi_id
    else:
        record = model.get_by_bi_id(0)
        assert not record
