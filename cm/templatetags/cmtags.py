# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Template tags
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.template.defaulttags import URLNode,register
##
## Act as django's standard {%url%} node.
## Add <module>:<app>: to view name when missed
##
class CMURLNode(URLNode):
    def render(self,context):
        if ":" not in self.view_name:
            # Append <module>:<app>: to view name when missed
            app=context["app"]
            self.view_name="%s:%s:%s"%(app.module,app.app,self.view_name)
        return super(CMURLNode,self).render(context)

def cm_url(parser,token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return CMURLNode(viewname, args, kwargs, asvar)
cm_url=register.tag(cm_url)