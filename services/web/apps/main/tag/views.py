# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.tag application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.main.models.tag import Tag
from noc.core.translation import ugettext as _


class TagApplication(ExtDocApplication):
    """
    Tag application
    """
    title = _("Tag")
    # menu = [_("Setup"), _("Tag")]
    model = Tag
    query_fields = ["tag"]

    @view(url="^ac_lookup/", method=["GET"], access=True)
    def api_ac_lookup(self, request):
        """
        Legacy AutoCompleteTags widget support
        :param request:
        :return:
        """
        if "query" not in request.GET:
            # If not query - return all
            tags = Tag.objects.filter()
        else:
            q = request.GET["query"]
            tags = Tag.objects.filter(tag__startswith=q)
        return {
            "data": [{"id": t.tag, "label": t.tag} for t in tags],
            "total": tags.count(),
            "success": True
        }
