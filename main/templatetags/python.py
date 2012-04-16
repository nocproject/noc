# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## python and pyrule tags
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import template


##
## Parsers
##
def do_python(parser, token):
    """
    {% python %}
    ...
    {% endpython %}
    :param parser:
    :param token:
    :return:
    """
    nodelist = parser.parse(("endpython",))
    parser.delete_first_token()
    return PythonNode(nodelist)


##
## Renderers
##
class PythonNode(template.Node):
    def __init__(self, nodelist):
        py_code = nodelist.render({}).replace("\r", "")
        self.code = compile(py_code, "string", "exec")

    def t_render(self, s):
        self.output += [s]

    def t_rendernl(self, s):
        self.output += [s, "\n"]

    def render(self, context):
        self.output = []
        # Prepare block context
        ctx = {
            "render": self.t_render,
            "rendernl": self.t_rendernl,
            "context": context
        }
        # Execute block
        exec self.code in ctx
        # Render output
        return "".join(self.output)


register = template.Library()
register.tag("python", do_python)
