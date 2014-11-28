# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.ref application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Django modules
from django.db import models
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.interfaces import interface_registry
from noc.sa.models import profile_registry
from noc.lib.stencil import stencil_registry
from noc import settings
from noc.main.models.notification import USER_NOTIFICATION_METHOD_CHOICES
from noc.pm.probes.base import probe_registry
from noc.pm.models.metrictype import MetricType


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
        return sorted(({"id": n, "label": n} for n in profile_registry.classes),
                      key=lambda x: x["label"])

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
        for f in os.listdir("static/pkg/codemirror/theme"):
            if f.endswith(".css"):
                t = f[:-4]
                r += [{
                    "id": t,
                    "label": t
                }]
        return r

    def build_unotificationmethod(self):
        return sorted(({"id": s[0], "label": s[1]}
                       for s in USER_NOTIFICATION_METHOD_CHOICES),
                      key=lambda x: x["label"])

    def build_probehandler(self):
        def f(k, v):
            solution = None
            if k.startswith("noc.solutions."):
                p = k.split(".")
                solution = "%s.%s" % (p[2], p[3])
            metrics = sorted(
                (
                    {
                        "id": mtc[m],
                        "label": m
                    } for m in v._METRICS if m in mtc
                ), key=lambda x: x["label"]
            )

            r = {
                "id": k,
                "label": v.TITLE if v.TITLE else k,
                "description": v.DESCRIPTION if v.DESCRIPTION else None,
                "form": v.CONFIG_FORM if v.CONFIG_FORM else None,
                "solution": solution,
                "metrics": metrics,
                "tags": v.TAGS
            }
            return r

        # Metric type cache
        mtc = dict(
            (n, str(i))
            for i, n in MetricType.objects.values_list("id", "name")
        )
        #
        return sorted(
            (
                f(k, v)
                for k, v in probe_registry.probe_classes.iteritems()
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

