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
from typing import Dict, Any, Optional, List, Set, Union

# Third-party modules
import bson
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
    EnumField,
)
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.reporter.types import (
    ReportConfig,
    Parameter,
    ReportBand,
    ReportQuery,
    Template as TemplateCfg,
    BandCondition,
    BandFormat as BandFormatCfg,
    ROOT_BAND,
    BandOrientation,
)
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
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
        choices=[
            "integer",
            "string",
            "date",
            "model",
            "model_multi",
            "choice",
            "combo-choice",
            "bool",
            "fields_selector",
        ],
        required=True,
    )
    model_id = StringField()
    choices = ListField(StringField())
    required = BooleanField(default=False)
    default = StringField(required=False)
    hide = BooleanField(default=False)
    localization = DictField()

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "description": self.description,
            "label": self.label,
            "type": self.type,
            "hide": self.hide,
        }
        if self.model_id:
            r["model_id"] = self.model_id
        if self.choices:
            r["choices"] = self.choices
        if self.required:
            r["required"] = self.required
        if self.default:
            r["default"] = self.default
        return r


class Template(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    output_type = StringField()
    code = StringField(default="DEFAULT")
    content = FileField(required=False)
    output_name_pattern = StringField()
    is_alterable_output = BooleanField(default=True)
    has_preview = BooleanField(default=False)
    handler = StringField(default="simplereport", required=True)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "code": self.code,
            "output_type": self.output_type,
            "is_alterable_output": self.is_alterable_output,
            "has_preview": self.has_preview,
            "handler": self.handler,
        }
        if self.output_name_pattern:
            r["output_name_pattern"] = self.output_name_pattern
        return r


class Query(EmbeddedDocument):
    datasource = StringField()
    ds_query = StringField()
    json = StringField()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {}
        if self.datasource:
            r["datasource"] = self.datasource
        if self.ds_query:
            r["ds_query"] = self.ds_query
        if self.datasource:
            r["json"] = self.json
        return r


class BandFormat(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField(required=True)
    title_template = StringField()
    # Do not in table print
    is_header = BooleanField(default=False)
    column_format = ListField(DictField())

    @property
    def is_root(self) -> bool:
        return self.name == ROOT_BAND

    def __str__(self):
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "title_template": self.title_template,
        }
        if self.column_format:
            r["column_format"] = [x for x in self.column_format]
        if self.is_header:
            r["is_header"] = self.is_header
        return r


class Band(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    name = StringField()
    parent = StringField()
    orientation: "BandOrientation" = EnumField(BandOrientation)
    queries = EmbeddedDocumentListField(Query)
    condition_param = StringField(required=False)
    condition_value = StringField(required=False)

    @property
    def is_root(self) -> bool:
        return self.name == ROOT_BAND

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "orientation": self.orientation.value,
        }
        if self.parent:
            r["parent"] = self.parent
        if self.queries:
            r["queries"] = [x.json_data for x in self.queries]
        if self.condition_param and self.condition_value:
            r["condition_param"] = self.condition_param
            r["condition_value"] = self.condition_value
        return r


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
        "json_collection": "main.reports",
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
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _effective_perm_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Report"]:
        return Report.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["Report"]:
        return Report.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["Report"]:
        return Report.objects.filter(code=code).first()

    def get_localization(self, field: str, lang: Optional[str] = None):
        from noc.config import config

        lang = lang or config.language
        if field in self.localization:
            return self.localization[field].get(lang)

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "code": self.code,
            "hide": self.hide,
            "title": self.title,
        }
        if self.category:
            r["category"] = self.category
        if self.report_source:
            r["report_source"] = self.report_source
        if self.localization:
            r["localization"] = {ll: dd for ll, dd in self.localization.items()}
        if self.parameters:
            r["parameters"] = [p.json_data for p in self.parameters]
        if self.templates:
            r["templates"] = [p.json_data for p in self.templates]
        if self.bands:
            r["bands"] = [p.json_data for p in self.bands]
        if self.bands_format:
            r["bands_format"] = [p.json_data for p in self.bands_format]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "title",
                "description",
            ],
        )

    def get_json_path(self) -> str:
        return quote_safe_path(self.name.strip("*")) + ".json"

    @property
    def config(self) -> ReportConfig:
        return self.get_config()

    def get_config(self, pref_lang: Optional[str] = None) -> ReportConfig:
        params = []
        for p in self.parameters:
            params.append(
                Parameter(
                    name=p.name,
                    alias=p.label,
                    type=p.type,
                    required=p.required,
                    default_value=p.default,
                    model_id=p.model_id,
                )
            )
        b_format_cfg = {}
        for bf in self.bands_format:
            columns = []
            for cf in bf.column_format:
                *_, cf_name = cf["name"].rsplit(".", 1)
                cf["title"] = (
                    self.get_localization(f"columns.{cf_name}", lang=pref_lang) or cf["title"]
                )
                columns += [cf]
            b_format_cfg[bf.name] = BandFormatCfg(
                **{"title_template": bf.title_template, "columns": columns}
            )
        templates = {}
        for t in self.templates:
            templates[t.code] = TemplateCfg(
                code=t.code,
                output_type=t.output_type,
                formatter=t.handler,
                output_name_pattern=t.output_name_pattern,
                bands_format=b_format_cfg,
            )
        if self.report_source:
            return ReportConfig(
                name=self.name,
                bands=[ReportBand(name="Root", source=self.report_source)],
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

        bands = {ROOT_BAND: ReportBand(name=ROOT_BAND, children=[])}
        for b in self.bands:
            if b.name in bands:
                bands[b.name].queries = [
                    ReportQuery(name=b.name, datasource=q.datasource, query=q.ds_query)
                    for q in b.queries
                ]
            else:
                bands[b.name] = ReportBand(
                    name=b.name,
                    queries=[
                        ReportQuery(name=b.name, datasource=q.datasource, query=q.ds_query)
                        for q in b.queries
                    ],
                    conditions=(
                        [BandCondition(param=b.condition_param, value=b.condition_value)]
                        if b.condition_param
                        else None
                    ),
                )
            if b.name != ROOT_BAND:
                parent = b.parent or ROOT_BAND
                bands[b.name].parent = bands[parent].name
                # bands[parent].children += [bands[b.name]]

        return ReportConfig(
            name=self.name,
            bands=list(bands.values()),
            templates=templates,
            parameters=params,
        )

    def get_band_format(self, band: Optional[str] = None) -> "BandFormat":
        for bf in self.bands_format:
            if not band:
                return bf
            elif bf.name == band:
                return bf
        return None

    def get_band_columns(self, band: str = ROOT_BAND) -> Dict[str, List[str]]:
        from noc.core.datasources.loader import loader

        r = defaultdict(list)
        for b in self.bands:
            if b.name != band:
                continue
            for num, q in enumerate(b.queries):
                if not q.datasource:
                    continue
                ds = loader[q.datasource]
                r[q.datasource] = [f.name for f in ds.iter_ds_fields()]
                if not num:
                    # default
                    r[""] = [f.name for f in ds.iter_ds_fields()]
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
