# ----------------------------------------------------------------------
# Window Functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import math
import time
from typing import Any
from collections.abc import Callable

# NOC modules
from noc.core.handler import get_handler
import itertools

type Window = list[tuple[int, float]]
type WindowFunction = Callable[..., Any]

# Model choices for window functions
wf_choices: list[tuple[str, str]] = []
# name -> callable
functions: dict[str, WindowFunction] = {}


def window_function(name: str, description: str) -> Callable[[WindowFunction], WindowFunction]:
    """Register a window function.

    Args:
        name: Function name used in configuration.
        description: Human-readable function description.

    Returns:
        Decorator registering the function.
    """

    def wrapper(f: WindowFunction) -> WindowFunction:
        functions[name] = f
        return f

    wf_choices.append((name, description))
    return wrapper


def get_window_function(name: str) -> WindowFunction | None:
    """Get window function by name.

    Args:
        name: Registered function name.

    Returns:
        Window function callable or None if function is not found.
    """
    return functions.get(name)


@window_function("last", "Last Value")
def last(window: Window, *args: Any, **kwargs: Any) -> float:
    """Return the last measured value in the window.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Last value from the window.
    """
    return window[-1][1]


@window_function("sum", "Sum")
def wf_sum(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate sum of values within the window.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Sum of all values.
    """
    return float(sum(w[1] for w in window))


@window_function("avg", "Average")
def avg(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate average value within the window.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Average value.
    """
    return float(sum(w[1] for w in window)) / len(window)


def _percentile(window: Window, q: int) -> float:
    """Calculate percentile value.

    Args:
        window: Sequence of timestamp-value pairs.
        q: Percentile value from 0 to 100.

    Returns:
        Calculated percentile.
    """
    wl = sorted(w[1] for w in window)
    i = len(wl) * q // 100
    return wl[i]


@window_function("percentile", "Percentile")
def percentile(window: Window, config: str, *args: Any, **kwargs: Any) -> float:
    """Calculate configured percentile.

    Args:
        window: Sequence of timestamp-value pairs.
        config: Percentile value.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Calculated percentile.

    Raises:
        ValueError: If percentile value is invalid.
    """
    if not window:
        raise ValueError("Cannot calculate percentile for empty window")
    try:
        q = int(config)
    except ValueError:
        raise ValueError("Percentile must be integer")

    if q < 0 or q > 100:
        raise ValueError("Percentile must be >0 and <100")

    return _percentile(window, q)


@window_function("q1", "1st quartile")
def q1(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate the first quartile.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        25th percentile value.
    """
    return _percentile(window, 25)


@window_function("q2", "2nd quartile")
def q2(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate the second quartile.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        50th percentile value.
    """
    return _percentile(window, 50)


@window_function("q3", "3rd quartile")
def q3(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate the third quartile.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        75th percentile value.
    """
    return _percentile(window, 75)


@window_function("p95", "95% percentile")
def p95(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate the 95th percentile.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        95th percentile value.
    """
    return _percentile(window, 95)


@window_function("p99", "99% percentile")
def p99(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate the 99th percentile.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        99th percentile value.
    """
    return _percentile(window, 99)


@window_function("step_inc", "Step Increment")
def step_inc(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate total positive increments within the window.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Sum of all positive value changes.
    """
    values = [x[1] for x in window]
    return sum(x1 - x0 for x0, x1 in itertools.pairwise(values) if x1 > x0)


@window_function("step_dec", "Step Decrement")
def step_dec(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate total negative decrements within the window.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Sum of all negative value changes.
    """
    values = [x[1] for x in window]
    return sum(x0 - x1 for x0, x1 in itertools.pairwise(values) if x0 > x1)


@window_function("step_abs", "Step Absolute")
def step_abs(window: Window, *args: Any, **kwargs: Any) -> float:
    """Calculate total absolute change within the window.

    Args:
        window: Sequence of timestamp-value pairs.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Sum of absolute value changes.
    """
    values = [x[1] for x in window]
    return sum(abs(x1 - x0) for x0, x1 in itertools.pairwise(values))


@window_function("handler", "Handler")
def handler(
    window: Window,
    config: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Calculate window value using custom handler.

    Args:
        window: Sequence of timestamp-value pairs.
        config: Handler name.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Result returned by the handler.

    Raises:
        ValueError: If handler cannot be found.
    """
    h = get_handler(config)
    if not h:
        raise ValueError(f"Invalid handler {config}")
    return h(window)


@window_function("exp_decay", "Exponential Decay")
def exp_decay(
    window: Window,
    config: str,
    current_time: int | None = None,
    *args: Any,
    **kwargs: Any,
) -> float:
    """Calculate exponentially decayed value.

    The function applies exponential decay to each value based on
    the age of the measurement.

    Args:
        window: Sequence of timestamp-value pairs.
        config: Exponential decay constant.
        current_time: Reference timestamp. Defaults to current Unix time.
        *args: Additional arguments ignored by the function.
        **kwargs: Additional arguments ignored by the function.

    Returns:
        Weighted sum of values.

    Raises:
        ValueError: If decay constant is invalid.
    """
    if not window:
        return 0.0

    try:
        neg_lambda = -float(config)
    except ValueError:
        raise ValueError("lambda must be float")

    t = current_time or int(time.time())
    return sum(value * math.exp(neg_lambda * (t - ts)) for ts, value in window)
