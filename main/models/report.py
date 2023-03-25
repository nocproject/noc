# ---------------------------------------------------------------------
# Report model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from collections import defaultdict
from typing import Dict, Any, Optional, List, Set

# Third-party modules
from mongoengine.document import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    EmbeddedDocumentListField,
    BooleanField,
    ListField,
    DictField,
    FileField,
    MapField,
)
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.reporter.types import ReportConfig, Parameter, ReportBand, ReportQuery
from noc.core.reporter.types import Template as TemplateCfg
from noc.core.reporter.types import BandFormat as BandFormatCfg
from noc.aaa.models.user import User
from noc.aaa.models.group import Group

id_lock = Lock()
perm_lock = Lock()


class ReportParam(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField(required=True)
    description = StringField(required=False)
    label = StringField()
    type = StringField(
        choices=["integer", "string", "date", "model", "choice", "bool", "fields_selector"],
        required=True,
    )
    model_id = StringField()
    choices = ListField(StringField())
    required = BooleanField(default=False)
    default = StringField(required=False)
    localization = DictField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"name": self.name, "description": self.description}
        if self.default:
            r["default"] = self.default
        return r


class Template(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    output_type = StringField()
    code = StringField(default="DEFAULT")
    content = FileField(required=False)
    output_name_pattern = StringField()
    handler = StringField()


class Query(EmbeddedDocument):
    datasource = StringField()
    ds_query = StringField()
    json = StringField()


class BandFormat(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField(required=True)
    title_template = StringField()
    column_format = ListField(DictField())

    @property
    def is_root(self) -> bool:
        return self.name == "Root"

    def __str__(self):
        return self.name


class Band(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    parent = StringField()
    orientation = StringField(choices=["H", "V", "C", "U"])
    queries = EmbeddedDocumentListField(Query)

    @property
    def is_root(self) -> bool:
        return self.name == "Root"


class Permission(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)
    edit = BooleanField(default=True)  # Edit report settings
    launch = BooleanField(default=False)  # Run to


class Report(Document):
    meta = {
        "collection": "noc.reports",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "main.reportes",
        "json_unique_fields": ["name"],
    }

    # Report name
    name = StringField(required=True, unique=True)
    category = StringField()
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    report_format = StringField()
    #
    code = StringField()  # Optional code for REST access
    hide = BooleanField()  # Hide from ReportMenu
    title = StringField()  # Menu Title
    report_source = StringField()
    is_system = BooleanField(default=False)  # Report Is System Based
    allow_rest = BooleanField(default=False)  # Available report data from REST API
    #
    parameters: List["ReportParam"] = EmbeddedDocumentListField(ReportParam)
    templates: List["Template"] = EmbeddedDocumentListField(Template)
    bands: List["Band"] = EmbeddedDocumentListField(Band)
    bands_format: List["BandFormat"] = EmbeddedDocumentListField(BandFormat)
    #
    permissions = EmbeddedDocumentListField(Permission)
    localization = MapField(DictField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _effective_perm_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["Report"]:
        return Report.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Report"]:
        return Report.objects.filter(name=name).first()

    def get_localization(self, field: str, lang: Optional[str] = None):
        from noc.config import config

        lang = lang or config.language
        if field in self.localization:
            return self.localization[field].get(lang)

    @property
    def config(self) -> ReportConfig:
        params = []
        for p in self.parameters:
            params.append(
                Parameter(
                    name=p.name,
                    alias=p.label,
                    type=p.type,
                    required=p.required,
                    default_value=p.default,
                )
            )
        b_format_cfg = {}
        for bf in self.bands_format:
            b_format_cfg[bf.name] = BandFormatCfg(
                **{"title_template": bf.title_template, "columns": bf.column_format}
            )
        templates = {}
        for t in self.templates:
            templates[t.code] = TemplateCfg(
                code=t.code,
                output_type=t.output_type,
                formatter="simplereport",
                output_name_pattern=t.output_name_pattern,
                bands_format=b_format_cfg,
            )
        if self.report_source:
            return ReportConfig(
                name=self.name,
                root_band=ReportBand(name="Root", children=[], source=self.report_source),
                templates={
                    "DEFAULT": TemplateCfg(
                        code="DEFAULT",
                        output_type="html",
                        formatter="simplereport",
                        output_name_pattern="report1",
                        bands_format={},
                    )
                },
                parameters=params,
            )

        bands = {"Root": ReportBand(name="Root", children=[])}
        for b in self.bands:
            if b.name in bands:
                bands[b.name].queries = [
                    ReportQuery(name="q1", datasource=q.datasource, query=q.ds_query)
                    for q in b.queries
                ]
            else:
                bands[b.name] = ReportBand(
                    name=b.name,
                    queries=[
                        ReportQuery(name="q1", datasource=q.datasource, query=q.ds_query)
                        for q in b.queries
                    ],
                    children=[],
                )
            if b.name != "Root":
                parent = b.parent or "Root"
                bands[b.name].parent = bands[parent]
                bands[parent].children += [bands[b.name]]

        return ReportConfig(
            name=self.name,
            root_band=bands["Root"],
            templates=templates,
            parameters=params,
        )

    def get_band_format(self, band: str = "Root") -> "BandFormat":
        for bf in self.bands_format:
            if bf.name == band:
                return bf
        return None

    def get_band_columns(self, band: str = "Root") -> Dict[str, List[str]]:
        from noc.core.datasources.loader import loader

        r = defaultdict(list)
        for b in self.bands:
            if b.name != band:
                continue
            for num, q in enumerate(b.queries):
                if not q.datasource:
                    continue
                ds = loader[q.datasource]
                r[q.datasource] = [f.name for f in ds.fields]
                if not num:
                    # default
                    r[""] = [f.name for f in ds.fields]
            break
        return r

    def get_root_datasource(self):
        from noc.core.datasources.loader import loader

        for b in self.bands:
            if b.is_root and b.queries and b.queries[0].datasource:
                return loader[b.queries[0].datasource]
        return None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_effective_perm_cache"), lock=lambda _: perm_lock)
    def get_effective_permissions(cls, user) -> Set[str]:
        """
        Returns a set of effective user permissions,
        counting group and implied ones
        """
        if user.is_superuser:
            return {str(rid) for rid in Report.objects.scalar("id")}
        perms = set()
        for rid in Report.objects.filter(
            permissions__user=user.id,
            permissions__launch=True,
        ).scalar("id"):
            perms.add(str(rid))
        for rid in Report.objects.filter(
            permissions__group__in=list(user.groups.all().values_list("id", flat=True)),
            permissions__launch=True,
        ).scalar("id"):
            perms.add(str(rid))
        return perms
