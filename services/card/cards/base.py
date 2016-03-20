# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from jinja2 import Template


class BaseCard(object):
    default_template_name = "default"
    template_cache = {}  # name -> Template instance
    TEMPLATE_PATH = [
        "custom/services/card/templates/",
        "services/card/templates/"
    ]
    model = None

    def __init__(self, id):
        self.object = self.dereference(id)

    def dereference(self, id):
        try:
            return self.model.objects.get(pk=id)
        except self.model.DoesNotExist:
            return None

    def get_data(self):
        """
        Returns template data
        """
        return {}

    def get_template_name(self):
        """
        Calculate and return template name
        """
        return self.default_template_name

    def get_template(self):
        """
        Return Template instance
        """
        name = self.get_template_name()
        if name not in self.template_cache:
            self.template_cache[name] = None
            for p in self.TEMPLATE_PATH:
                tp = os.path.join(p, name + ".html.j2")
                if os.path.exists(tp):
                    with open(tp) as f:
                        self.template_cache[name] = Template(f.read())
        return self.template_cache[name]

    def render(self):
        template = self.get_template()
        if template:
            data = self.get_data()
            return template.render(**data)
        else:
            return None
