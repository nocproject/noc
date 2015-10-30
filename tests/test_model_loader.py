# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test model loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from nose2.tools import params
## NOC modules
from noc.models import iter_model_id, get_model, get_model_id


def test_iter_model_id():
    """ Check loader.iter_scripts() returns values """
    assert len(list(iter_model_id())) > 0


@params(*tuple(iter_model_id()))
def test_model_loading(model_id):
    """ Check model can be loaded """
    model = get_model(model_id)
    assert model, "Cannot load model %s" % model_id
    n_model_id = get_model_id(model)
    assert model_id == n_model_id, "Model ID mismatch for %s" % model_id
