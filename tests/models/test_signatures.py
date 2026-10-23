# ----------------------------------------------------------------------
# Test models' method signatures
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect

# Third-party modules
import pytest

# NOC modules
from .util import get_all_models
from noc.models import is_document, DB_MODEL_TYPE


def int_or_oid(x) -> str:
    if is_document(x):
        return "str | bson.objectid.ObjectId"
    return "int"


@pytest.mark.parametrize(
    ("name", "args"),
    [
        pytest.param(
            "get_by_id",
            [("oid", int_or_oid)],
            id="get_by_id",
        ),
        pytest.param(
            "get_by_name",
            [("name", "str")],
            id="get_by_name",
        ),
        pytest.param(
            "get_by_bi_id",
            [("bi_id", "int")],
            id="get_by_bi_id",
        ),
    ],
)
@pytest.mark.parametrize("model", get_all_models(), ids=lambda x: x.__name__)
def test_get_by_signatures(name: str, args, model: DB_MODEL_TYPE) -> None:
    method = getattr(model, name, None)
    if not method:
        pytest.skip(f"No {name} method")
    # Check classmethod
    assert method.__self__ is model, f"{name} must be @classmethod"
    # Check parameters signature
    sig = inspect.signature(method, eval_str=True)
    for param_name, param_type in args:
        assert param_name in sig.parameters, f"Parameter `{param_name}` is missed"
        param = sig.parameters[param_name]
        assert param.annotation is not inspect._empty, (
            f"Parameter `{param_name}` has no type annotation"
        )
        if inspect.isclass(param.annotation):
            pa = param.annotation.__name__
        else:
            pa = str(param.annotation)
        if callable(param_type):
            param_type = param_type(model)
        assert pa == param_type, (
            f"Parameter `{param_name}` must be `{param_type!s}`. Current is `{pa}`"
        )
    # Check return type signature
    assert sig.return_annotation == model | None, (
        f"{name}: return type must be {model.__name__} | None (has {sig.return_annotation!r})"
    )
