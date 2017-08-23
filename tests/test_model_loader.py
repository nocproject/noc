# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test model loader
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.models import iter_model_id, get_model, get_model_id


def test_iter_model_id():
    """
    Check loader.iter_scripts() returns values
    """
    total_models = len(list(iter_model_id()))
    assert total_models > 0


@pytest.fixture(params=iter_model_id())
def model_id(request):
    return request.param


def test_model_loading(model_id):
    """
    Check model referred by id can be loaded
    :param model_id:
    :return:
    """
    model = get_model(model_id)
    assert model is not None, "Cannot load model %s" % model_id


def test_model_id(model_id):
    """
    Check model has same model_id as referred
    """
    model = get_model(model_id)
    if model:
        real_model_id = get_model_id(model)
        assert real_model_id == model_id
