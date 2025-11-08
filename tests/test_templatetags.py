# ---------------------------------------------------------------------
# Template tags test
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import django.template
import pytest


PYTHON1_TPL = """
{% load python %}
Before:
x={{ x }}
y={{ y }}
{% python %}
context["x"] += 3
context["y"] = 2 * context["x"]
render("Python code completed")
{% endpython %}
x={{ x }}
y={{ y }}
"""

PYTHON1_OUT = """

Before:
x=1
y=
Python code completed
x=4
y=8
"""

PYTHON2_TPL = """
{% load python %}
{% python %}
for i in range(context["n"]):
    rendernl("Line #%d" % i)
{% endpython %}
"""

PYTHON2_OUT = """

Line #0
Line #1
Line #2

"""

PYTHON3_TPL = """
{% load python %}
{% var v1 internal %}
v={{v}}
{% python %}
context["v1"] = 2 * context["v"] + 3
{% endpython %}
v1={{v1}}
"""

PYTHON3_OUT = """


v=2

v1=7
"""


@pytest.mark.parametrize(
    ("template", "context", "expected"),
    [
        (PYTHON1_TPL, {"x": 1}, PYTHON1_OUT),
        (PYTHON2_TPL, {"n": 3}, PYTHON2_OUT),
        (PYTHON3_TPL, {"v": 2}, PYTHON3_OUT),
    ],
)
def test_templatetags(template, context, expected):
    ctx = django.template.Context(context)
    result = django.template.Template(template).render(ctx)
    assert result == expected
