# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RPSL Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.contrib import admin
# NOC modules
from noc.cm.repoapp import RepoApplication
from noc.cm.models.rpsl import RPSL
from noc.core.translation import ugettext as _


class RPSLAdmin(admin.ModelAdmin):
    list_display = ["repo_path", "last_modified", "status"]
    search_fields = ["repo_path"]


class RPSLApplication(RepoApplication):
    repo = "rpsl"
    model = RPSL
    model_admin = RPSLAdmin
    menu = _("RPSL Objects")
