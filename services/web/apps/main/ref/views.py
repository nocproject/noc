# ---------------------------------------------------------------------
# main.ref application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import re
import operator

# Third-party modules
from django.apps import apps
from mongoengine.base.common import _document_registry

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.services.web.base.site import site
from noc.core.interface.loader import loader as interface_loader
from noc.core.stencil import stencil_registry
from noc.core.profile.loader import loader as profile_loader
from noc.core.script.loader import loader as script_loader
from noc.core.checkers.loader import loader as checker_loader
from noc.core.window import wf_choices
from noc.core.topology.types import ShapeOverlayPosition, ShapeOverlayForm
from noc.core.topology.loader import loader as topo_loader
from noc.core.mx import MessageType, MESSAGE_HEADERS
from noc.core.datasources.loader import loader as ds_loader
from noc.core.protodcsources.loader import loader as pds_loader
from noc.main.reportsources.loader import loader as rds_loader
from noc.models import iter_model_id
from noc import settings
from noc.services.web.apps.kb.parsers.loader import loader as kbparser_loader
from noc.main.models.notificationgroup import USER_NOTIFICATION_METHOD_CHOICES


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
    NOC_SOUND_PATH = "ui/pkg/nocsound"

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
        return [{"id": n, "label": n} for n in interface_loader.iter_interfaces()]

    def build_profile(self):
        """
        Profile names
        :return: (profile name, profile name)
        """
        return [{"id": n, "label": n} for n in profile_loader.iter_profiles()]

    def build_script(self):
        """
        Profile names
        :return: (script name, script name)
        """
        s = set(x.split(".")[-1] for x in script_loader.iter_scripts())
        return [{"id": n, "label": n} for n in sorted(s)]

    def build_stencil(self):
        """
        Stencils
        :return:
        """
        return list(
            sorted(
                ({"id": s[0], "label": s[1]} for s in stencil_registry.choices),
                key=lambda x: x["label"],
            )
        )

    def build_model(self):
        """
        Model Names
        :return:
        """
        return list(
            sorted(
                ({"id": m._meta.db_table, "label": m._meta.db_table} for m in apps.get_models()),
                key=lambda x: x["label"],
            )
        )

    def build_modcol(self):
        """
        Models and collections
        """
        r = []
        # Models
        r += [
            {
                "id": m._meta.db_table,
                "label": "%s.%s" % (m._meta.app_label, m.__name__),
                "table": m._meta.db_table,
            }
            for m in apps.get_models()
        ]
        # Collections
        r += [
            {
                "id": c._get_collection_name(),
                "label": "%s.%s" % (c.__module__.split(".")[1], n),
                "collection": c._get_collection_name(),
            }
            for n, c in _document_registry.items()
            if c._get_collection_name()
        ]
        return list(sorted(r, key=lambda x: x["label"]))

    def build_ulanguage(self):
        """
        User languages
        :return:
        """
        return [
            {"id": lang[0], "label": lang[1]}
            for lang in sorted(settings.LANGUAGES, key=operator.itemgetter(1))
        ]

    rx_fa_glyph = re.compile(r"\.fa-([^:]+):before\{content:", re.MULTILINE | re.DOTALL)

    def build_glyph(self):
        r = [{"id": "", "label": "---"}]
        if os.path.exists(self.FA_CSS_PATH):
            with open(self.FA_CSS_PATH) as f:
                for match in self.rx_fa_glyph.finditer(f.read()):
                    glyph = match.group(1)
                    r += [{"id": "fa fa-%s" % glyph, "label": glyph}]
        return r

    def build_sound(self):
        r = [{"id": "", "label": "---"}]
        if os.path.isdir(self.NOC_SOUND_PATH):
            for f in sorted(os.listdir(self.NOC_SOUND_PATH)):
                if f.endswith(".mp3"):
                    r += [{"id": f[:-4], "label": f[:-4]}]
        return r

    def build_unotificationmethod(self):
        return list(
            sorted(
                ({"id": s[0], "label": s[1]} for s in USER_NOTIFICATION_METHOD_CHOICES),
                key=lambda x: x["label"],
            )
        )

    def build_windowfunction(self):
        return [{"id": x[0], "label": x[1]} for x in sorted(wf_choices, key=operator.itemgetter(1))]

    def _build_report(self):
        return list(
            sorted(
                ({"id": r_id, "label": r.title} for r_id, r in site.iter_predefined_reports()),
                key=operator.itemgetter("label"),
            )
        )

    def build_modelid(self):
        return [{"id": x, "label": x} for x in sorted(iter_model_id())]

    def build_kbparser(self):
        return [{"id": x, "label": x} for x in sorted(kbparser_loader)]

    def build_soposition(self):
        return [{"id": x.value, "label": x.name} for x in ShapeOverlayPosition]

    def build_soform(self):
        return [{"id": x.value, "label": x.name} for x in ShapeOverlayForm]

    def build_messagetype(self):
        return [
            {"id": x.value, "label": x.name}
            for x in sorted([m for m in MessageType], key=lambda x: x.name)
        ]

    def build_messageheader(self):
        return [{"id": x, "label": x} for x in sorted(MESSAGE_HEADERS)]

    def build_check(self):
        """Checkers names"""
        return list(
            sorted(
                ({"id": s[0], "label": s[1]} for s in checker_loader.choices()),
                key=lambda x: x["label"],
            )
        )

    def build_topologygen(self):
        """
        Topology Generators name
        :return:
        """
        r = []
        for name in topo_loader:
            topo_gen = topo_loader[name]
            r += [{"id": name, "label": topo_gen.header or name}]
        return r  # list(sorted(r))

    def build_datasource(self):
        """
        Datasource name
        :return:
        """
        r = []
        for name in ds_loader:
            ds = ds_loader[name]
            if not ds:
                continue
            r += [{"id": name, "label": ds.name}]
        return r  # list(sorted(r))

    def build_reportsource(self):
        """
        ReportSource name
        :return:
        """
        r = []
        for name in rds_loader:
            repo_source = rds_loader[name]
            if not repo_source:
                continue
            r += [{"id": name, "label": repo_source.name}]
        return r  # list(sorted(r))

    def build_protocoldiscriminatorsource(self):
        """
        Protocol Discriminator Source name
        :return:
        """
        r = []
        for name in pds_loader:
            ds = pds_loader[name]
            if not ds:
                continue
            r += [{"id": name, "label": ds.name}]
        return r  # list(sorted(r))

    @view(url=r"^(?P<ref>\S+)/lookup/$", method=["GET"], access=True, api=True)
    def api_lookup(self, request, ref=None):
        if ref not in self.refs:
            if ref == "report":
                self.refs["report"] = self._build_report()
            else:
                return self.response_not_found()
        # return self.refs[ref]
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        limit = q.get(self.limit_param)
        # page = q.get(self.page_param)
        start = q.get(self.start_param)
        format = q.get(self.format_param)
        query = q.get(self.query_param)
        if "id" in q:
            data = [x for x in self.refs[ref] if str(x["id"]) == q["id"]]
        elif query:
            ql = query.lower()
            data = [x for x in self.refs[ref] if ql in x["label"].lower()]
        else:
            data = [x for x in self.refs[ref]]
        total = len(data)
        if start is not None and limit is not None:
            data = data[int(start) : int(start) + int(limit)]
        if format == "ext":
            return {"total": total, "success": True, "data": data}
        return data
