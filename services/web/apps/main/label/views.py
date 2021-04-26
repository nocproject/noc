# ----------------------------------------------------------------------
# main.label application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from collections import defaultdict

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.main.models.label import Label
from noc.core.translation import ugettext as _


class LabelApplication(ExtDocApplication):
    """
    Label application
    """

    title = "Label"
    menu = [_("Setup"), _("Labels")]
    glyph = "tag"
    model = Label
    query_condition = "icontains"

    @view(url="^ac_lookup/", method=["GET"], access=True)
    def api_ac_lookup(self, request):
        """
        Legacy AutoCompleteTags widget support
        :param request:
        :return:
        """
        query = request.GET.get("__query")
        labels_filter = {
            str(k): True if v[0] == "true" else False
            for k, v in request.GET.lists()
            if k.startswith("enable_")
        }
        if query:
            labels_filter["name__icontains"] = query
        # If not query - return all
        labels = Label.objects.filter(**labels_filter).order_by("id")
        labels = [
            {
                "id": ll.name,
                "is_protected": ll.is_protected,
                "name": ll.name,
                "scope": ll.name.rsplit("::", 1)[0] if ll.is_scoped else "",
                "value": ll.name.split("::")[-1],
                "bg_color1": "#%x" % ll.bg_color1,
                "fg_color1": "#%x" % ll.fg_color1,
                "bg_color2": "#%x" % ll.bg_color2,
                "fg_color2": "#%x" % ll.fg_color2,
            }
            for ll in labels
            if not (ll.is_wildcard or ll.is_matched)
        ]
        return {
            "data": labels,
            "total": len(labels),
            "success": True,
        }

    @view(url="^lookup_tree/", method=["GET"], access=True)
    def api_labels_lookup_tree(self, request):
        leafs = defaultdict(list)
        level = 1
        labels_filter = {}
        query = request.GET.get("__query")
        if query:
            labels_filter["name__icontains"] = query
        # If not query - return all
        for ll in Label.objects.filter(**labels_filter).order_by("id"):
            if ll.is_wildcard:
                # wildcards[ll.name] =
                continue
            path = ll.name.split("::")
            if ll.is_matched:
                parent = "::".join(path[: -level - 1])
            else:
                parent = "::".join(path[:-level])

            leafs[parent].append(
                {
                    "text": ll.name,
                    # "type": f.type,
                    "parent": parent,
                    "id": str(ll.name),
                    "leaf": True,
                    "checked": False,
                }
            )

        return self.render_json(
            {"text": "root", "children": [{"text": lf, "children": leafs[lf]} for lf in leafs]}
        )
