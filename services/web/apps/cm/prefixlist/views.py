# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PrefixList Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.contrib import admin
# NOC modules
from noc.cm.repoapp import RepoApplication
from noc.cm.models.prefixlist import PrefixList
from noc.core.translation import ugettext as _


class PrefixListAdmin(admin.ModelAdmin):
    list_display = ["repo_path", "last_modified", "status"]
    search_fields = ["repo_path"]


class PrefixListApplication(RepoApplication):
    repo = "prefix-list"
    model = PrefixList
    model_admin = PrefixListAdmin
    menu = _("Prefix Lists")
