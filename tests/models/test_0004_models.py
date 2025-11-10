# ----------------------------------------------------------------------
# Test models fields
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import cachetools
import pytest
from django.db.models import BooleanField
from django.db.models.fields import NOT_PROVIDED

# NOC modules
from noc.models import get_model_id
from .util import get_models


@cachetools.cached({})
def get_fields():
    r = []
    for model in get_models():
        for f in model._meta.fields:
            r += [(get_model_id(model), f.name, f)]
    return r


@pytest.mark.parametrize(
    ("model_id", "field_name", "field"), [x for x in get_fields() if isinstance(x[2], BooleanField)]
)
def test_boolean_defaults(model_id, field_name, field):
    assert field.default is not None and field.default != NOT_PROVIDED, (
        "BooleanField default must be set to either True or False"
    )


@pytest.mark.parametrize("model", get_models())
def test_tucked_pants(model):
    assert hasattr(model, "_tucked_pants"), "Model must be subclass of NOCModel"
