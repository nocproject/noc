# ----------------------------------------------------------------------
# Test all models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.models import get_model_id, get_model, iter_model_id
from .util import get_models, get_documents


def test_iter_model_id():
    """
    Check iter_model_id is not empty
    """
    assert any(iter_model_id()), "Empty model id"


@pytest.mark.parametrize("model_id", iter_model_id())
def test_model_loading(model_id):
    """
    Check model referred by id can be loaded
    :param model_id:
    :return:
    """
    model = get_model(model_id)
    assert model is not None, "Cannot load model %s" % model_id


@pytest.mark.parametrize("model_id", iter_model_id())
def test_model_id(model_id):
    """
    Check model has same model_id as referred
    """
    model = get_model(model_id)
    assert model
    real_model_id = get_model_id(model)
    assert real_model_id == model_id


@pytest.mark.parametrize("model", get_models())
def test_model_meta(model):
    assert model._meta


@pytest.mark.parametrize("model", get_models())
def test_model_app_label(model):
    assert model._meta.app_label


@pytest.mark.parametrize("model", get_models())
def test_model_db_table(model):
    assert model._meta.db_table


@pytest.mark.parametrize("model", get_documents())
def test_document_meta(model):
    assert model._meta


@pytest.mark.parametrize("model", get_documents())
def test_document_allow_inheritance(model):
    assert (
        model._meta.get("allow_inheritance") is None
    ), "'allow_inheritance' is obsolete and must not be used"


@pytest.mark.parametrize("model", get_documents())
def test_document_strict(model):
    assert not model._meta.get("strict", True), "Document must be declared as {'strict': False}"


@pytest.mark.parametrize("model", get_documents())
def test_document_auto_create_index(model):
    assert not model._meta.get(
        "auto_create_index", True
    ), "Index autocreation must not be used (Use auto_create_index: False)"
