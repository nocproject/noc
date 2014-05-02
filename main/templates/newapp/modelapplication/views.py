# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## {{module}}.{{app}} application
##----------------------------------------------------------------------
## Copyright (C) 2007-{{year}} The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import {{base_class}}, view
from {{modelimport}} import {{model}}


class {{model}}Application({{base_class}}):
    """
    {{model}} application
    """
    title = "{{model}}"
    menu = "Setup | {{model}}"
    model = {{model}}
