# ---------------------------------------------------------------------
# main.tag application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
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
    default_ordering = ["tag"]

    @view(url="^ac_lookup/", method=["GET"], access=True)
    def api_ac_lookup(self, request):
        """
        Legacy AutoCompleteTags widget support
        :param request:
        :return:
        """
        query = request.GET.get("__query")
        if query:
            tags = Tag.objects.filter(tag__icontains=query).order_by("tag")
        else:
            # If not query - return all
            tags = Tag.objects.filter().order_by("tag")
        return {
            "data": [{"id": t.tag, "label": t.tag} for t in tags],
            "total": tags.count(),
            "success": True,
        }
