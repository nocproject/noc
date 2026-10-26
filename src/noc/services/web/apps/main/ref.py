# ---------------------------------------------------------------------
# main.ref application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import os

# Third-party modules
from django.apps import apps
from django.http import HttpRequest
from mongoengine.base.common import _document_registry

# NOC modules
from noc import settings
from noc.core.checkers.loader import loader as checker_loader
from noc.core.datasources.base import data_source_loader
from noc.core.mx import MESSAGE_HEADERS, MessageType
from noc.core.profile.loader import loader as profile_loader
from noc.core.protodcsources.base import discriminator_source_loader
from noc.core.reporter.formatter.base import data_formatter_loader
from noc.core.script.loader import loader as script_loader
from noc.core.topology.base import loader as topo_loader
from noc.core.vlanroles import VLANRole
from noc.core.window import wf_choices
from noc.inv.models.objectmodel import ContainerType
from noc.main.models.messageroute import MessageRoute
from noc.main.models.notificationgroup import USER_NOTIFICATION_METHOD_CHOICES
from noc.main.reportsources.loader import loader as rds_loader
from noc.models import iter_model_id
from noc.services.web.apps.kb.parsers.base import kb_parser_loader
from noc.services.web.base.extapplication import ExtApplication, api
from noc.services.web.base.site import site


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

    def __init__(self, *args, **kwargs) -> None:
        ExtApplication.__init__(self, *args, **kwargs)
        self.refs = {}  # Name -> [(key, value)]
        # Fill refs
        for h in dir(self):
            if h.startswith("build_"):
                self.refs[h[6:]] = getattr(self, h)()

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
        s = {x.split(".")[-1] for x in script_loader.iter_scripts()}
        return [{"id": n, "label": n} for n in sorted(s)]

    def build_model(self):
        """
        Model Names
        :return:
        """
        return sorted(
            ({"id": m._meta.db_table, "label": m._meta.db_table} for m in apps.get_models()),
            key=lambda x: x["label"],
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
                "label": f"{m._meta.app_label}.{m.__name__}",
                "table": m._meta.db_table,
            }
            for m in apps.get_models()
        ]
        # Collections
        r += [
            {
                "id": c._get_collection_name(),
                "label": f"{c.__module__.split('.')[1]}.{n}",
                "collection": c._get_collection_name(),
            }
            for n, c in _document_registry.items()
            if c._get_collection_name()
        ]
        return sorted(r, key=lambda x: x["label"])

    def build_ulanguage(self):
        """
        User languages
        :return:
        """
        return [
            {"id": lang[0], "label": lang[1]}
            for lang in sorted(settings.LANGUAGES, key=operator.itemgetter(1))
        ]

    def build_sound(self):
        r = [{"id": "", "label": "---"}]
        if os.path.isdir(self.NOC_SOUND_PATH):
            for f in sorted(os.listdir(self.NOC_SOUND_PATH)):
                if f.endswith(".mp3"):
                    r.append({"id": f[:-4], "label": f[:-4]})
        return r

    def build_unotificationmethod(self):
        r = []
        for s in USER_NOTIFICATION_METHOD_CHOICES:
            r.append({"id": s[0], "label": s[1]})
        for mx in MessageRoute.objects.filter(register_notification_method=True):
            r.append({"id": str(mx.id), "label": str(mx.name)})
        return sorted(r, key=lambda x: x["label"])

    def build_windowfunction(self):
        return [{"id": x[0], "label": x[1]} for x in sorted(wf_choices, key=operator.itemgetter(1))]

    def _build_report(self):
        return sorted(
            ({"id": r_id, "label": r.title} for r_id, r in site.iter_predefined_reports()),
            key=operator.itemgetter("label"),
        )

    def build_modelid(self):
        return [{"id": x, "label": x} for x in sorted(iter_model_id())]

    def build_kbparser(self):
        return [{"id": x, "label": x} for x in sorted(kb_parser_loader)]

    def build_messagetype(self):
        return [{"id": x.value, "label": x.name} for x in sorted(MessageType, key=lambda x: x.name)]

    def build_messageheader(self):
        return [{"id": x, "label": x} for x in sorted(MESSAGE_HEADERS)]

    def build_check(self):
        """Checkers names"""
        return sorted(
            ({"id": s[0], "label": s[1]} for s in checker_loader.choices()),
            key=lambda x: x["label"],
        )

    def build_topologygen(self):
        """
        Topology Generators name
        :return:
        """
        r = []
        for name in topo_loader:
            topo_gen = topo_loader[name]
            r.append({"id": name, "label": topo_gen.header or name})
        return r  # list(sorted(r))

    def build_datasource(self):
        """
        Datasource name
        :return:
        """
        r = []
        for name in data_source_loader:
            ds = data_source_loader.get(name)
            if not ds or not getattr(ds, "name", None):
                continue
            r.append({"id": name, "label": ds.name})
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
            r.append({"id": name, "label": repo_source.name})
        return r  # list(sorted(r))

    def build_reportformatter(self):
        """
        ReportSource name
        :return:
        """
        r = []
        for name in data_formatter_loader:
            repo_fmt = data_formatter_loader.get(name)
            if not repo_fmt:
                continue
            r.append({"id": name, "label": repo_fmt.label or name})
        return r  # list(sorted(r))

    def build_protocoldiscriminatorsource(self):
        """
        Protocol Discriminator Source name
        :return:
        """
        r = []
        for name in discriminator_source_loader:
            ds = discriminator_source_loader.get(name)
            if not ds:
                continue
            r.append({"id": name, "label": ds.name})
        return r  # list(sorted(r))

    def build_vlanrole(self):
        """Vlan Roles Lookup"""
        return sorted([{"id": x.value, "label": x.name} for x in VLANRole], key=lambda x: x["id"])

    def build_containertype(self):
        """Container type loolup"""
        return [{"id": x.value, "label": x.name} for x in ContainerType]

    @api.get(r"^(?P<ref>\S+)/lookup/$", access=True)
    def api_lookup(self, request: HttpRequest, ref=None):
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
            data = list(self.refs[ref])
        total = len(data)
        if start is not None and limit is not None:
            data = data[int(start) : int(start) + int(limit)]
        if format == "ext":
            return {"total": total, "success": True, "data": data}
        return data
