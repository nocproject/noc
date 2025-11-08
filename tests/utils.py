# ----------------------------------------------------------------------
# Testing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Protocol, Type
import inspect


def check_protocol(proto: Protocol, impl: Type[object]) -> None:
    """Check implementation follows protocol."""

    def check_method(name: str, proto_value) -> None:
        # Check method is present
        target_method = getattr(impl, name, None)
        assert target_method, f"{name} is not defined"
        # Check method is callable
        assert callable(target_method), f"{name}: must be callable"
        # Protocol signature
        proto_sig = inspect.signature(proto_value)
        # Implementation signature
        target_sig = inspect.signature(target_method)
        # Compare parameters
        proto_params = list(proto_sig.parameters.values())
        target_params = list(target_sig.parameters.values())
        assert len(proto_params) == len(target_params), (
            f"{name}: parameters length mismatch: {len(proto_params)} != {len(target_params)}"
        )
        for i, (pp, tp) in enumerate(zip(proto_params, target_params)):
            # Compare kinds
            assert pp.kind == tp.kind, (
                f"{name}: parameter {i} kind mismatch: {pp.kind} != {tp.kind}"
            )
            # Compare names
            assert pp.name == tp.name, (
                f"{name}: parameter {i} name mismatch: {pp.name} != {tp.name}"
            )
            # Compare annotations
            if pp.annotation is not inspect._empty:
                assert tp.annotation is not inspect._empty, f"{name}: parameter {i} has no typing"
            else:
                assert pp.annotation == tp.annotation, f"{name}: parameter {i} type mismatch"
        # Compare return types
        assert proto_sig.return_annotation == target_sig.return_annotation, (
            f"{name}: return type mismatch {proto_sig.return_annotation} != {target_sig.return_annotation}"
        )

    for name, proto_value in inspect.getmembers(proto):
        if not name.startswith("_"):
            check_method(name, proto_value)
