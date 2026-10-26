# ----------------------------------------------------------------------
# CPU Affinity tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.affinity import AFF_AUTO, AFF_NONE, BaseController


def affinity_controller(affinity: set[int]) -> type[BaseController]:
    """Create an affinity controller with predefined CPU affinity."""

    class TestAffinityController(BaseController):
        @classmethod
        def get_affinity(cls):
            return affinity

    return TestAffinityController


@pytest.mark.parametrize(
    ("aff", "expected"),
    [
        ("", AFF_NONE),
        ("none", AFF_NONE),
        ("auto", AFF_AUTO),
        ("  none ", AFF_NONE),
        ("auto    ", AFF_AUTO),
    ],
)
def test_parse_affinity_sentinel(aff: str, expected: object) -> None:
    assert BaseController.parse_affinity(aff) is expected


@pytest.mark.parametrize(
    ("aff", "expected"),
    [
        ("0", {0}),
        ("0,1", {0, 1}),
        ("0,2,4", {0, 2, 4}),
        ("1,3,5,7", {1, 3, 5, 7}),
        # With spaces
        (" 0", {0}),
        (" 0  ", {0}),
        ("0, 1", {0, 1}),
        ("0,2, 4", {0, 2, 4}),
        ("1,3    ,5,   7    ", {1, 3, 5, 7}),
    ],
)
def test_parse_affinity_mask(aff: str, expected: set[int]) -> None:
    assert BaseController.parse_affinity(aff) == expected


@pytest.mark.parametrize(
    "aff",
    [
        "foo",
        "0,foo",
        "1.5",
        "-",
    ],
)
def test_parse_affinity_invalid(aff: str) -> None:
    with pytest.raises(ValueError):
        BaseController.parse_affinity(aff)


@pytest.mark.parametrize("aff", ["", "none"])
def test_effective_affinity_none(aff: str) -> None:
    controller = affinity_controller({0, 1, 2})

    assert controller.effective_affinity(aff) is AFF_NONE


@pytest.mark.parametrize("aff", ["auto", "0,1"])
def test_effective_affinity_unavailable(aff: str) -> None:
    assert BaseController.effective_affinity(aff) is AFF_NONE


@pytest.mark.parametrize("aff", ["auto", "0,1"])
def test_effective_affinity_empty(aff: str) -> None:
    controller = affinity_controller(set())
    assert controller.effective_affinity(aff) is AFF_NONE


@pytest.mark.parametrize("mask", [{0}, {0, 1}, {1, 3, 7}])
def test_effective_affinity_auto(mask: set[int]) -> None:
    controller = affinity_controller(mask)
    result = controller.effective_affinity("auto")
    assert isinstance(result, set)
    assert len(result) == 1
    assert result <= mask


@pytest.mark.parametrize(
    ("mask", "requested", "expected"),
    [
        ({0, 1, 2}, "0", {0}),
        ({0, 1, 2}, "0,1", {0, 1}),
        ({0, 1, 2}, "1,3", {1}),
        ({0, 1, 2}, "0,2,4", {0, 2}),
        ({0, 1, 2}, "0,1,2", {0, 1, 2}),
    ],
)
def test_effective_affinity_intersection(
    mask: set[int], requested: str, expected: set[int]
) -> None:
    controller = affinity_controller(mask)
    assert controller.effective_affinity(requested) == expected


@pytest.mark.parametrize(
    ("mask", "requested"),
    [
        ({0, 1}, "2"),
        ({0, 1}, "2,3"),
        ({4, 5}, "0,1,2"),
    ],
)
def test_effective_affinity_no_intersection(mask: set[int], requested: str) -> None:
    controller = affinity_controller(mask)
    assert controller.effective_affinity(requested) is AFF_NONE
