# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## {% tags ... %}
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import template
from noc.lib.widgets import tags_list

register=template.Library()

class TagsNode(template.Node):
    def __init__(self,object):
        self.object=template.Variable(object)
    def render(self,context):
        return tags_list(self.object.resolve(context))

def do_tags(parser,token):
    try:
        tag_name,object=token.split_contents()
    except ValueError:
        raise template.SyntaxError("%r tag requires a single argument"%token.contents.split()[0])
    return TagsNode(object)

register.tag("tags",do_tags)
