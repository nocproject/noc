# ----------------------------------------------------------------------
# main.label application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
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
from noc.models import LABEL_MODELS


class LabelApplication(ExtDocApplication):
    """
    Label application
    """

    title = "Label"
    menu = [_("Labels")]
    glyph = "tag"
    model = Label
    query_condition = "icontains"
    query_fields = ["name__contains", "description__contains"]

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

    def field_is_noc_builtin(self, o: "Label"):
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
        if "set_wildcard" in q:
            q["name__endswith"] = "*"
            del q["set_wildcard"]
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
        q = {}
        query = request.GET.get("__query")
        if query:
            q["name__icontains"] = query
        allow_models, allow_matched, allow_wildcard, allow_user = [], False, False, True
        enable_models_map = {v: k for k, v in LABEL_MODELS.items()}
        for k, v in request.GET.lists():
            print("K,v", k, v)
            if k == "allow_models":
                allow_models += v
                continue
            if k.startswith("enable_") and k in enable_models_map:
                allow_models += [enable_models_map[k]]
            elif k == "allow_wildcard" and "true" in v:
                allow_wildcard = True
            elif k == "allow_matched" and "true" in v:
                allow_matched = True
            elif k == "allow_user" and "false" in v:
                allow_user = False
        # If not query - return all
        qs = Label.objects.filter(**q)
        if not allow_wildcard:
            qs = qs.filter(name__not__endswith="*")
        if not allow_matched:
            qs = qs.filter(name__not__endswith="=")
        if allow_models and not allow_matched:
            qs = qs.filter(allow_models__in=allow_models)
        labels = []
        for ll in qs.order_by("name"):
            #                 if (allow_user and not ll.is_wildcard and not ll.is_matched)
            if (
                allow_wildcard
                and allow_models
                and not frozenset(allow_models).intersection(set(ll.allow_models))
            ):
                continue
            if not allow_user and not ll.is_matched and not ll.is_wildcard and not ll.is_protected:
                continue
            labels += [
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
