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
def do_var(parser, token):
    """
    {% var <name> internal %}
    :param parser:
    :param token:
    :return:
    """
    try:
        tag, name, vartype = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%s tag requires two arguments" % (
            token.contents.split()[0]))
    return VarNode(name, vartype)


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
    try:
        return PythonNode(nodelist)
    except SyntaxError, why:
        raise template.TemplateSyntaxError("Python syntax error: %s" % why)


##
## Renderers
##
class VarNode(template.Node):
    def __init__(self, name, vartype):
        self.name = name
        self.vartype = vartype

    def render(self, context):
        return ""


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
register.tag("var", do_var)
register.tag("python", do_python)
