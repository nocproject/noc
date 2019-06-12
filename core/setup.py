# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Django setup wrapper
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


def setup():
    from django.conf import settings
    from django.apps import apps
    # apps.populate([x for x in settings.INSTALLED_APPS if not x.startswith("noc.")])
    apps.populate(settings.INSTALLED_APPS)
