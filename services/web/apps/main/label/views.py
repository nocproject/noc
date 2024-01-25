# ----------------------------------------------------------------------
# main.label application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict

# NOC modules
from noc.sa.interfaces.base import ColorParameter
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.label import Label
from noc.core.translation import ugettext as _


class LabelApplication(ExtDocApplication):
    """
    Label application
    """

    title = "Label"
    menu = [_("Labels")]
    glyph = "tag"
    model = Label
    query_condition = "icontains"

    clean_fields = {
        "bg_color1": ColorParameter(),
        "bg_color2": ColorParameter(),
        "fg_color1": ColorParameter(),
        "fg_color2": ColorParameter(),
    }

    not_builtin_re = re.compile(r"^(?!noc\:\:)")
    builtin_re = re.compile(r"^noc\:\:")

    not_matched_re = re.compile(r"[^=<>&]$")
    matched_re = re.compile(r"[=<>&]$")

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if not isinstance(o, Label):
            return r
        for s, model_id in Label.ENABLE_MODEL_ID_MAP.items():
            r[s] = model_id in o.allow_models
        return r

    def field_is_builtin(self, o: "Label"):
        return bool(o.is_builtin)

    def field_is_scoped(self, o: "Label"):
        return bool(o.is_scoped)

    def field_is_wildcard(self, o: "Label"):
        return bool(o.is_wildcard)

    def field_is_matched(self, o: "Label"):
        return bool(o.is_matched)

    def cleaned_query(self, q):
        q = super().cleaned_query(q)
        if "is_builtin_labels" in q:
            q["name"] = self.builtin_re if q["is_builtin_labels"] == "true" else self.not_builtin_re
            del q["is_builtin_labels"]
        else:
            q["name"] = self.not_builtin_re
        if "is_matched" in q:
            q["name"] = self.matched_re if q["is_matched"] == "true" else self.not_matched_re
            del q["is_matched"]
        return q

    def clean(self, data):
        data["allow_models"] = []
        for k in list(data):
            if k in Label.ENABLE_MODEL_ID_MAP:
                if data.pop(k):
                    data["allow_models"].append(Label.ENABLE_MODEL_ID_MAP[k])
        return super().clean(data)

    @view(url="^ac_lookup/", method=["GET"], access=True)
    def api_ac_lookup(self, request):
        """
        Legacy AutoCompleteTags widget support
        :param request:
        :return:
        """
        query = request.GET.get("__query")
        allow_matched = ("allow_matched", ["true"]) in request.GET.lists()
        allow_wildcard = ("allow_wildcard", ["true"]) in request.GET.lists()
        allow_user = not ("allow_user", ["false"]) in request.GET.lists()
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
                "scope": ll.scope,
                "name": ll.name,
                "value": ll.value,
                "badges": ll.badges,
                "bg_color1": f"#{ll.bg_color1:06x}",
                "fg_color1": f"#{ll.fg_color1:06x}",
                "bg_color2": f"#{ll.bg_color2:06x}",
                "fg_color2": f"#{ll.fg_color2:06x}",
            }
            for ll in labels
            if (allow_user and not ll.is_wildcard and not ll.is_matched)
            or (allow_matched and ll.is_matched)
            or (allow_wildcard and ll.is_wildcard)
            # if not (ll.is_wildcard or (ll.is_matched and not allow_matched))
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
                    "name": ll.name,
                    # "type": f.type,
                    "parent": parent,
                    "id": str(ll.name),
                    "leaf": True,
                    "is_protected": False,
                    "scope": ll.scope,
                    "value": ll.value,
                    "badges": ll.badges,
                    "bg_color1": "#%x" % ll.bg_color1,
                    "fg_color1": "#%x" % ll.fg_color1,
                    "bg_color2": "#%x" % ll.bg_color2,
                    "fg_color2": "#%x" % ll.fg_color2,
                    # "checked": False,
                }
            )

        return self.render_json(
            {
                "name": "root",
                "is_protected": False,
                "leaf": False,
                "children": [
                    {"name": lf, "leaf": False, "is_protected": False, "children": leafs[lf]}
                    for lf in leafs
                ],
            }
        )
