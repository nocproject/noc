# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Template tags test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import template
## NOC modules
from noc.lib.test import NOCTestCase

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

class TemplateTestCase(NOCTestCase):
    def render(self, tpl, context={}):
        ctx = template.Context(context)
        return template.Template(tpl).render(ctx)

    def test_python(self):
        """
        {% python %} tag test
        :return:
        """
        self.assertEquals(self.render(PYTHON1_TPL, {"x": 1}),
                          PYTHON1_OUT)
        self.assertEquals(self.render(PYTHON2_TPL, {"n": 3}),
                          PYTHON2_OUT)
        self.assertEquals(self.render(PYTHON3_TPL, {"v": 2}),
                          PYTHON3_OUT)
