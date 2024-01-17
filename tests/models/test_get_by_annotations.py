# ----------------------------------------------------------------------
# Checking get_by_XX methods annotations validation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect
from typing import Optional, ForwardRef

# Third-party modules
from bson import ObjectId
import pytest

# NOC modules
from .util import get_models, get_documents


@pytest.mark.parametrize("model", get_models())
def test_models(model):
    if hasattr(model, "get_by_id"):
        sig = inspect.signature(model.get_by_id)
        # parameters
        if "id" not in sig.parameters:
            pytest.fail(f"Method '{model.__name__}.get_by_id' must have 'id' parameter")
        assert sig.parameters["id"].annotation is int
        # result
        assert sig.return_annotation == Optional[ForwardRef(model.__name__)]
    if hasattr(model, "get_by_bi_id"):
        sig = inspect.signature(model.get_by_bi_id)
        # parameters
        if "id" not in sig.parameters:
            pytest.fail(f"Method '{model.__name__}.get_by_bi_id' must have 'id' parameter")
        assert sig.parameters["id"].annotation is int
        # result
        assert sig.return_annotation == Optional[ForwardRef(model.__name__)]


@pytest.mark.parametrize("document", get_documents())
def test_documents(document):
    if hasattr(document, "get_by_id"):
        sig = inspect.signature(document.get_by_id)
        # parameters
        if "id" not in sig.parameters:
            pytest.fail(f"Method '{document.__name__}.get_by_id' must have 'id' parameter")
        assert sig.parameters["id"].annotation is ObjectId
        # result
        assert sig.return_annotation == Optional[ForwardRef(document.__name__)]
    if hasattr(document, "get_by_bi_id"):
        sig = inspect.signature(document.get_by_bi_id)
        # parameters
        if "id" not in sig.parameters:
            pytest.fail(f"Method '{document.__name__}.get_by_bi_id' must have 'id' parameter")
        assert sig.parameters["id"].annotation is int
        # result
        assert sig.return_annotation == Optional[ForwardRef(document.__name__)]
    if hasattr(document, "get_by_code"):
        sig = inspect.signature(document.get_by_code)
        # parameters
        if "code" not in sig.parameters:
            pytest.fail(f"Method '{document.__name__}.get_by_code' must have 'code' parameter")
        assert sig.parameters["code"].annotation is str
        # result
        assert sig.return_annotation == Optional[ForwardRef(document.__name__)]
