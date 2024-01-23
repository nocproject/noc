# ----------------------------------------------------------------------
# Checking get_by_XX methods annotations validation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect
from typing import Optional, ForwardRef, Union

# Third-party modules
from bson import ObjectId
import pytest

# NOC modules
from noc.models import is_document
from .util import get_all_models


@pytest.mark.parametrize("model", get_all_models())
def test_get_by_id(model):
    if not hasattr(model, "get_by_id"):
        raise pytest.skip("Not implemented")
    sig = inspect.signature(model.get_by_id)
    # parameters
    if is_document(model):
        if "oid" not in sig.parameters:
            pytest.fail(f"Method '{model.__name__}.get_by_id' must have 'oid' parameter")
        assert sig.parameters["oid"].annotation == Union[str, ObjectId]
    else:
        if "id" not in sig.parameters:
            pytest.fail(f"Method '{model.__name__}.get_by_id' must have 'id' parameter")
        assert sig.parameters["id"].annotation is int
    # result
    assert sig.return_annotation == Optional[ForwardRef(model.__name__)]


@pytest.mark.parametrize("model", get_all_models())
def test_get_by_bi_id(model):
    if not hasattr(model, "get_by_bi_id"):
        raise pytest.skip("Not implemented")
    sig = inspect.signature(model.get_by_bi_id)
    # parameters
    if "bi_id" not in sig.parameters:
        pytest.fail(f"Method '{model.__name__}.get_by_bi_id' must have 'bi_id' parameter")
    assert sig.parameters["bi_id"].annotation is int
    # result
    assert sig.return_annotation == Optional[ForwardRef(model.__name__)]
