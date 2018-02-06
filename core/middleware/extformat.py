# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ExtFormat middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class ExtFormatMiddleware(object):
    """
    Set request.is_extjs when __format=ext found in request
    """
    def process_request(self, request):
        if request.GET and request.GET.get("__format") == "ext":
            request.is_extjs = True
        elif request.POST and request.POST.get("__format") == "ext":
            request.is_extjs = True
        else:
            request.is_extjs = False
