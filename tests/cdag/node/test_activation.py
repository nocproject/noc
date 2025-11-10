# ----------------------------------------------------------------------
# Activation functions test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    ("fn", "config", "x", "expected"),
    [
        # Indicator
        ("indicator", {}, -1, 0),
        ("indicator", {}, 0, 1),
        ("indicator", {}, 1, 1),
        ("indicator", {"false_level": -3}, -1, -3),
        ("indicator", {"true_level": 3}, 1, 3),
        # Logistic
        ("logistic", {}, -1, 0.2689414213699951),
        ("logistic", {}, -1.0, 0.2689414213699951),
        ("logistic", {}, 0, 0.5),
        ("logistic", {}, 0.0, 0.5),
        ("logistic", {}, 1, 0.7310585786300049),
        ("logistic", {}, 1.0, 0.7310585786300049),
        ("logistic", {"k": 0.0}, 0.0, None),
        # ReLU
        ("relu", {}, -1, 0),
        ("relu", {}, -1.0, 0.0),
        ("relu", {}, 0, 0),
        ("relu", {}, 1, 1),
        ("relu", {}, 1.0, 1.0),
        ("relu", {}, 2.0, 2.0),
        # Softplus
        ("softplus", {}, -1.0, 0.31326168751822286),
        ("softplus", {}, 0.0, 0.6931471805599453),
        ("softplus", {}, 1.0, 1.3132616875182228),
        ("softplus", {}, 2.0, 2.1269280110429727),
        ("softplus", {"k": 2}, -1.0, 0.0634640055214863),
        ("softplus", {"k": 2}, 0.0, 0.34657359027997264),
        ("softplus", {"k": 2}, 1.0, 1.0634640055214863),
        ("softplus", {"k": 2}, 2.0, 2.0090749639589047),
        ("softplus", {"k": 0}, -1.0, None),
    ],
)
def test_activation_node(fn, config, x, expected):
    cdag = NodeCDAG(fn, config=config)
    assert cdag.is_activated() is False
    cdag.activate("x", x)
    x_act = expected is not None
    assert cdag.is_activated() is x_act
    value = cdag.get_value()
    if expected is None:
        assert value is None
    else:
        assert value == pytest.approx(expected, rel=1e-4)
