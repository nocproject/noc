# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django URL dispatcher.
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.app import site,patterns

urlpatterns=patterns("",
    ('^$',                     'django.views.generic.simple.redirect_to', {'url' : '/main/index/'}),
    # For debugging purposes only. Overriden by HTTP server directives
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static'}),
    (r'^doc/(?P<path>.*)$',    'django.views.static.serve', {'document_root': 'share/doc/users_guide/html/'}),
)+site.urls

handler404="noc.main.views.handler404"