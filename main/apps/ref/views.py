# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.ref application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import re
## Django modules
from django.db import models
## Third-party modules
from mongoengine.base.common import _document_registry
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.interfaces.base import interface_registry
from noc.lib.stencil import stencil_registry
from noc import settings
from noc.main.models.notificationgroup import USER_NOTIFICATION_METHOD_CHOICES
from noc.cm.validators.base import validator_registry
from noc.core.profile.loader import loader as profile_loader


class RefAppplication(ExtApplication):
    """
    main.ref application
    """
    ignored_params = ["_dc"]
    page_param = "__page"
    start_param = "__start"
    limit_param = "__limit"
    sort_param = "__sort"
    format_param = "__format"  # List output format
    query_param = "__query"

    FA_CSS_PATH = "ui/pkg/fontawesome/css/font-awesome.min.css"

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        self.refs = {}  # Name -> [(key, value)]
        # Fill refs
        for h in dir(self):
            if h.startswith("build_"):
                self.refs[h[6:]] = getattr(self, h)()

    def build_interface(self):
        """
        Interface names
        :return: (interface name, interface name)
        """
        return sorted(({"id": n, "label": n} for n in interface_registry),
                      key=lambda x: x["label"])

    def build_profile(self):
        """
        Profile names
        :return: (profile name, profile name)
        """
        return [{
            "id": n,
            "label": n
        } for n in profile_loader.iter_profiles()]

    def build_stencil(self):
        """
        Stencils
        :return:
        """
        return sorted(({"id": s[0], "label": s[1]} for s in stencil_registry.choices),
            key=lambda x: x["label"])

    def build_model(self):
        """
        Model Names
        :return:
        """
        return sorted(({"id": m._meta.db_table,
                        "label": m._meta.db_table}
            for m in models.get_models()),
            key=lambda x: x["label"])

    def build_modcol(self):
        """
        Models and collections
        """
        r = []
        # Models
        r += [{
            "id": m._meta.db_table,
            "label": "%s.%s" % (m._meta.app_label, m.__name__),
            "table": m._meta.db_table
        } for m in models.get_models()]
        # Collections
        r += [
            {
                "id": c._get_collection_name(),
                "label": "%s.%s" % (c.__module__.split(".")[1], n),
                "collection": c._get_collection_name()
            } for n, c in _document_registry.iteritems()
            if c._get_collection_name()]
        return sorted(r, key=lambda x: x["label"])

    def build_ulanguage(self):
        """
        User languages
        :return:
        """
        return sorted(
            {"id": l[0], "label": l[1]}
            for l in settings.LANGUAGES
        )

    def build_theme(self):
        """
        UI Themes
        :return:
        """
        conf = settings.config
        themes = [t[:-5] for t in conf.options("themes")
                  if (t.endswith(".name") and
                      conf.getboolean("themes", "%s.enabled" % t[:-5]))]
        return sorted([
            {
                "id": t,
                "label": conf.get("themes", "%s.name" % t)
            } for t in themes],
            key=lambda x: x["label"].lower()
        )

    def build_cmtheme(self):
        """
        CodeMirror themes
        """
        r = [{
            "id": "default",
            "label": "default"
        }]
        if os.path.isdir("ui/pkg/codemirror/theme"):
            for f in os.listdir("ui/pkg/codemirror/theme"):
                if f.endswith(".css"):
                    t = f[:-4]
                    r += [{
                        "id": t,
                        "label": t
                    }]
        return r

    rx_fa_glyph = re.compile(
        r"\.fa-([^:]+):before\{content:",
        re.MULTILINE | re.DOTALL
    )

    def build_glyph(self):
        r = [{
            "id": "",
            "label": "---"
        }]
        if os.path.exists(self.FA_CSS_PATH):
            with open(self.FA_CSS_PATH) as f:
                for match in self.rx_fa_glyph.finditer(f.read()):
                    glyph = match.group(1)
                    r += [{
                        "id": "fa fa-%s" % glyph,
                        "label": glyph
                    }]
        return r

    def build_unotificationmethod(self):
        return sorted(({"id": s[0], "label": s[1]}
                       for s in USER_NOTIFICATION_METHOD_CHOICES),
                      key=lambda x: x["label"])

    def build_validator(self):
        def f(k, v):
            solution = None
            if k.startswith("noc.solutions."):
                p = k.split(".")
                solution = "%s.%s" % (p[2], p[3])
            tags = []
            if v.is_object():
                tags += ["OBJECT"]
            if v.is_interface():
                tags += ["INTERFACE"]
            if v.is_subinterface():
                tags += ["SUBINTERFACE"]
            if v.TAGS:
                tags += v.TAGS
            r = {
                "id": k,
                "label": v.TITLE if v.TITLE else k,
                "description": v.DESCRIPTION if v.DESCRIPTION else None,
                "form": v.CONFIG_FORM if v.CONFIG_FORM else None,
                "solution": solution,
                "tags": tags
            }
            return r

        return sorted(
            (
                f(k, v)
                for k, v in validator_registry.validators.items()
                if v.TITLE
            ),
            key=lambda x: x["label"]
        )

    @view(url="^(?P<ref>\S+)/lookup/$", method=["GET"], access=True, api=True)
    def api_lookup(self, request, ref=None):
        if ref not in self.refs:
            return self.response_not_found()
        # return self.refs[ref]
        q = dict((str(k), v[0] if len(v) == 1 else v)
                 for k, v in request.GET.lists())
        limit = q.get(self.limit_param)
        # page = q.get(self.page_param)
        start = q.get(self.start_param)
        format = q.get(self.format_param)
        query = q.get(self.query_param)
        if "id" in q:
            data = [x for x in self.refs[ref]
                    if str(x["id"]) == q["id"]]
        elif query:
            ql = query.lower()
            data = [x for x in self.refs[ref]
                    if ql in x["label"].lower()]
        else:
            data = [x for x in self.refs[ref]]
        total = len(data)
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        if format == "ext":
            return {
                "total": total,
                "success": True,
                "data": data
            }
        else:
            return data

