# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test model loader
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import operator
# Third-party modules
import pytest
# NOC modules
from noc.models import iter_model_id, get_model, get_model_id, is_document


def test_iter_model_id():
    """
    Check loader.iter_scripts() returns values
    """
    total_models = len(list(iter_model_id()))
    assert total_models > 0


@pytest.fixture(params=iter_model_id())
def model_id(request):
    return request.param


@pytest.mark.dependency(name="test_model_loading")
def test_model_loading(model_id):
    """
    Check model referred by id can be loaded
    :param model_id:
    :return:
    """
    model = get_model(model_id)
    assert model is not None, "Cannot load model %s" % model_id


@pytest.mark.dependency(name="test_model_id", depends=["test_model_loading"])
def test_model_id(model_id):
    """
    Check model has same model_id as referred
    """
    model = get_model(model_id)
    if model:
        real_model_id = get_model_id(model)
        assert real_model_id == model_id


@pytest.mark.dependency(depends=["test_model_loading"])
def test_model_meta(model_id):
    model = get_model(model_id)
    assert model
    if is_document(model):
        pytest.skip("Not a model")
    assert model._meta
    assert model._meta.app_label
    assert model._meta.db_table


@pytest.mark.dependency(depends=["test_model_loading"])
def test_document_meta(model_id):
    model = get_model(model_id)
    assert model
    if not is_document(model):
        pytest.skip("Not a document")
    assert model._meta.get("allow_inheritance") is None, "'allow_inheritance' is obsolete and must not be used"
    assert not model._meta.get("strict", True), "Document must be declared as {'strict': False}"
    assert not model._meta.get("auto_create_index", True), "Index autocreation must not be used (Use auto_create_index: False)"


def get_model_references():
    """
    Build model reference map
    :return: [(model id, [(remote model, remote field), ..], ..]
    """
    from noc.lib.nosql import PlainReferenceField, ForeignKeyField
    from noc.core.model.fields import DocumentReferenceField
    from django.db.models import ForeignKey

    def add_ref(model, ref_model, ref_field):
        model_id = get_model_id(model)
        refs[model_id] += [(ref_model, ref_field)]

    refs = defaultdict(list)  # model -> [(ref model, ref field)]
    for model_id in iter_model_id():
        model = get_model(model_id)
        if not model:
            continue
        if is_document(model):
            # mongoengine document
            for fn in model._fields:
                f = model._fields[fn]
                if isinstance(f, PlainReferenceField):
                    add_ref(f.document_type, model_id, fn)
                elif isinstance(f, ForeignKeyField):
                    add_ref(f.document_type, model_id, fn)
        else:
            # Django model
            for f in model._meta.fields:
                if isinstance(f, ForeignKey):
                    add_ref(f.rel.to, model_id, f.name)
                elif isinstance(f, DocumentReferenceField):
                    add_ref(f.document, model_id, f.name)
    return [(m, refs[m]) for m in refs]


@pytest.fixture(scope="session", params=get_model_references(), ids=operator.itemgetter(0))
def model_refs(request):
    return request.param


def test_on_delete(model_refs):
    model_id, refs = model_refs
    model = get_model(model_id)
    assert model
    assert hasattr(model, "_on_delete"), "Must have @on_delete_check decorator (Referenced from %s)" % refs
    x_checks = set(model._on_delete["check"])
    x_checks |= set(model._on_delete["clean"])
    x_checks |= set(model._on_delete["delete"])
    for c in x_checks:
        assert isinstance(c, tuple), "@on_delete_check decorator must contain only tuples"
        assert len(c) == 2, "@on_delete_check decorator must contain only two-item tuples"
    for mn, fn in refs:
        assert (mn, fn) in x_checks, "@on_delete_check decorator must refer to (\"%s\", \"%s\")" % (mn, fn)
