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
from noc.models import is_document


def int_or_oid(x) -> str:
    if is_document(x):
        return "typing.Union[str, bson.objectid.ObjectId]"
    return "int"


@pytest.mark.parametrize(
    ("name", "is_classmethod", "args", "return_type"),
    [
        pytest.param(
            "get_by_id",
            True,
            [("oid", int_or_oid)],
            "typing.Optional[ForwardRef('{model}')]",
            id="get_by_id",
        ),
        pytest.param(
            "get_by_name",
            True,
            [("name", "str")],
            "typing.Optional[ForwardRef('{model}')]",
            id="get_by_name",
        ),
        pytest.param(
            "get_by_bi_id",
            True,
            [("bi_id", "int")],
            "typing.Optional[ForwardRef('{model}')]",
            id="get_by_bi_id",
        ),
    ],
)
@pytest.mark.parametrize("model", get_all_models(), ids=lambda x: x.__name__)
def test_signatures(name: str, is_classmethod: bool, args, return_type, model) -> None:
    method = getattr(model, name, None)
    if not method:
        pytest.skip(f"No {name} method")
    # Check classmethod
    if is_classmethod:
        assert method.__self__ is model, f"{name} must be @classmethod"
    # Check parameters signature
    sig = inspect.signature(method)
    for param_name, param_type in args:
        assert param_name in sig.parameters, f"Parameter `{param_name}` is missed"
        param = sig.parameters[param_name]
        assert (
            param.annotation is not inspect._empty
        ), f"Parameter `{param_name}` has no type annotation"
        if inspect.isclass(param.annotation):
            pa = param.annotation.__name__
        else:
            pa = str(param.annotation)
        if callable(param_type):
            param_type = param_type(model)
        assert (
            pa == param_type
        ), f"Parameter `{param_name}` must be `{param_type!s}`. Current is `{pa}`"
    # Check return type signature
    expanded_type = return_type.replace("{model}", model.__name__)
    assert (
        str(sig.return_annotation) == expanded_type
    ), f"Return type must be {expanded_type} (has {sig.return_annotation!s})"
