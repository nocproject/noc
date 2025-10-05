# ----------------------------------------------------------------------
# Window Functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import math
import time

# NOC modules
from noc.core.handler import get_handler
import itertools

# Model choices for window functions
wf_choices = []
# name -> callable
functions = {}


def window_function(name, description):
    """
    Window function decorator
    :param f:
    :return:
    """

    def wrapper(f):
        functions[name] = f
        return f

    global wf_choices, functions
    wf_choices += [(name, description)]
    return wrapper


def get_window_function(name):
    """
    Returns window function by name
    """
    return functions.get(name)


@window_function("last", "Last Value")
def last(window, *args, **kwargs):
    """
    Returns last measured value
    :param window:
    :return:
    """
    return window[-1][1]


@window_function("sum", "Sum")
def wf_sum(window, *args, **kwargs):
    """
    Returns sum of values within window
    :param window:
    :return:
    """
    return float(sum(w[1] for w in window))


@window_function("avg", "Average")
def avg(window, *args, **kwargs):
    """
    Returns window average
    :param window:
    :return:
    """
    return float(sum(w[1] for w in window)) / len(window)


def _percentile(window, q):
    """
    Calculate percentile
    :param window:
    :param q:
    :return:
    """
    wl = sorted(w[1] for w in window)
    i = len(wl) * q // 100
    return wl[i]


@window_function("percentile", "Percentile")
def percentile(window, config, *args, **kwargs):
    """
    Calculate percentile
    :param window:
    :param config:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        q = int(config)
    except ValueError:
        raise ValueError("Percentile must be integer")
    if q < 0 or q > 100:
        raise ValueError("Percentile must be >0 and <100")
    return _percentile(window, q)


@window_function("q1", "1st quartile")
def q1(window, *args, **kwargs):
    """
    1st quartile
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    return _percentile(window, 25)


@window_function("q2", "2st quartile")
def q2(window, *args, **kwargs):
    """
    1st quartile
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    return _percentile(window, 50)


@window_function("q3", "3st quartile")
def q3(window, *args, **kwargs):
    """
    1st quartile
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    return _percentile(window, 75)


@window_function("p95", "95% percentile")
def p95(window, *args, **kwargs):
    """
    1st quartile
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    return _percentile(window, 95)


@window_function("p99", "99% percentile")
def p99(window, *args, **kwargs):
    """
    1st quartile
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    return _percentile(window, 99)


@window_function("step_inc", "Step Increment")
def step_inc(window, *args, **kwargs):
    """
    Sum of all increments within window
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    values = [x[1] for x in window]
    return sum(x1 - x0 for x0, x1 in itertools.pairwise(values) if x1 > x0)


@window_function("step_dec", "Step Decrement")
def step_dec(window, *args, **kwargs):
    """
    Sum of all decrements within window
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    values = [x[1] for x in window]
    return sum(x0 - x1 for x0, x1 in itertools.pairwise(values) if x0 > x1)


@window_function("step_abs", "Step Absolute")
def step_abs(window, *args, **kwargs):
    """
    Sum of all absolute changes within window
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    values = [x[1] for x in window]
    return sum(abs(x1 - x0) for x0, x1 in itertools.pairwise(values))


@window_function("handler", "Handler")
def handler(window, config, *args, **kwargs):
    """
    Calculate via handler
    :param window:
    :param config:
    :param args:
    :param kwargs:
    :return:
    """
    h = get_handler(config)
    if not h:
        raise ValueError("Invalid handler %s" % config)
    return h(window)


@window_function("exp_decay", "Exponential Decay")
def exp_decay(window, config, current_time=None, *args, **kwargs):
    """
    Exponential decay.
    :param window:
    :param config: Exponential decay constant
    :param current_time:
    :param args:
    :param kwargs:
    :return:
    """
    if not window:
        return 0.0
    try:
        neg_lambda = -float(config)
    except ValueError:
        raise ValueError("lambda must be float")
    t = current_time or int(time.time())
    return sum(value * math.exp(neg_lambda * (t - ts)) for ts, value in window)
