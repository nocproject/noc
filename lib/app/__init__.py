# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from site import *
from access import *
from application import *
from modelapplication import *
from treeapplication import *
from extapplication import *
from extmodelapplication import *
from extdocapplication import *
from noc.settings import config, IS_WEB
##
## Setup Context Processor.
## Used via TEMPLATE_CONTEXT_PROCESSORS variable in settings.py
## Adds "setup" variable to context.
## "setup" is a hash of
##      "installation_name"
##
def setup_processor(request):
    favicon_url=config.get("customization", "favicon_url")
    if favicon_url.endswith(".png"):
        favicon_mime="image/png"
    elif favicon_url.endswith(".jpg") or favicon_url.endswith(".jpeg"):
        favicon_mime="image/jpeg"
    else:
        favicon_mime=None
    
    return {
        "setup" : {
            "installation_name" : config.get("customization", "installation_name"),
            "logo_url"          : config.get("customization", "logo_url"),
            "logo_width"        : config.get("customization", "logo_width"),
            "logo_height"       : config.get("customization", "logo_height"),
            "favicon_url"       : favicon_url,
            "favicon_mime"      : favicon_mime,
        }
    }
