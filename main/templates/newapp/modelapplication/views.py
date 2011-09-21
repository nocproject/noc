# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## {{module}}.{{app}} application
##----------------------------------------------------------------------
## Copyright (C) 2007-{{year}} The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.{{module}}.models import {{model}}


class {{model}}Application(ExtModelApplication):
    """
    {{model}} application
    """
    title = "{{model}}"
    menu = "Setup | {{model}}"
    model = {{model}}
