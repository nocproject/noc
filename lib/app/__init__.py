# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application classes
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

#from __future__ import with_statement
#from django.template import RequestContext
#from django.shortcuts import render_to_response
#from django.http import HttpResponse,HttpResponseRedirect,HttpResponseForbidden,HttpResponseNotFound
#from django.utils.simplejson.encoder import JSONEncoder
#from django.conf.urls.defaults import *
#from django.core.urlresolvers import *
#from django.contrib.auth import REDIRECT_FIELD_NAME
#from django.conf import settings
#from django.utils.http import urlquote
#from django.contrib import admin as django_admin
#from django.db import connection
#from noc.settings import INSTALLED_APPS,config
#from noc.lib.debug import error_report
#from noc.lib.access import *
#import logging,os,glob,types,re,urllib

##
from site import *
from access import *
from application import *
from modelapplication import *
from noc.settings import config
##
## Setup Context Processor.
## Used via TEMPLATE_CONTEXT_PROCESSORS variable in settings.py
## Adds "setup" variable to context.
## "setup" is a hash of
##      "installation_name"
##
def setup_processor(request):
    return {
        "setup" : {
            "installation_name" : config.get("customization","installation_name"),
            "logo_url"          : config.get("customization","logo_url"),
            "logo_width"        : config.get("customization","logo_width"),
            "logo_height"       : config.get("customization","logo_height"),
        }
    }
##
## Load all applications
##
site.autodiscover()