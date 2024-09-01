# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Iterable, ForwardRef

# Third-party modules
from pydantic import BaseModel, ConfigDict

# NOC modules
from noc.models import get_model, is_document

ROOT_BAND = "Root"


class BandOrientation(enum.Enum):
    HORIZONTAL = "H"
    VERTICAL = "V"
    CROSS = "C"
    UNDEFINED = "U"


class OutputType(enum.Enum):
    HTML = "html"
    XLSX = "xlsx"
    CSV = "csv"
    CSV_ZIP = "csv+zip"
    SSV = "ssv"
    PDF = "pdf"


class ColumnAlign(enum.Enum):
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    MASK = 4


class FieldFormat(enum.Enum):
    BOOL = "bool"
    INTEGER = "int"
    URL = "url"
    PERCENT = "percent"
    DATETIME = "datetime"
    NUMERIC = "numeric"
    STRING = "string"


class ReportQuery(BaseModel):
    name: str
    datasource: Optional[str] = None  # DataSource Name
    query: Optional[str] = None  # DataFrame query
    params: Dict[str, Any] = None
    json_data: Optional[str] = None
    transpose: bool = False


ReportBand = ForwardRef("ReportBand")


class BandCondition(BaseModel):
    param: str
    value: str

    def __str__(self):
        return f"{self.param} == {self.value}"


class ReportBand(BaseModel):
    name: str
    queries: Optional[List[ReportQuery]] = None
    source: Optional[str] = None
    parent: Optional["ReportBand"] = None  # Parent Band
    orientation: BandOrientation = "H"  # Relevant only for xlsx template
    children: Optional[List["ReportBand"]] = None
    conditions: Optional[List[BandCondition]] = None

    def __str__(self):
        return self.name

    def __init__(self, **data):
        super().__init__(**data)
        self.children = self.children or []
        for c in self.children:
            c.parent = self

    @property
    def has_children(self) -> bool:
        return bool(self.children)

    def iter_nester(self) -> Iterable["ReportBand"]:
        for c in self.children:
            yield c
            yield from c.iter_nester()

    def is_match(self, params: Dict[str, Any]) -> bool:
        if not self.conditions:
            return True
        for c in self.conditions:
            if c.param in params:
                return c.value in params[c.param]
        return True


class ColumnFormat(BaseModel):
    """Format settings for column"""

    name: str
    title: Optional[str] = None
    align: ColumnAlign = ColumnAlign(1)
    format_type: Optional[str] = None
    total: str = None  # Calculate summary stat
    total_label: str = "Total"


class BandFormat(BaseModel):
    """
    Configuration for autogenerate template
    """

    title_template: Optional[str] = None  # Title format for Section row
    columns: Optional[List[ColumnFormat]] = None  # ColumnName -> ColumnFormat


class Template(BaseModel):
    """
    Attributes:
        code: ReportTemplate.DEFAULT_TEMPLATE_CODE
        formatter: Formatter name. Or Autodetect by content
        bands_format: BandName -> BandFormat. For autoformat BandsData
    """

    output_type: OutputType
    code: str = "DEFAULT"
    # documentPath: str
    content: Optional[bytes] = None
    formatter: Optional[str] = None
    bands_format: Optional[Dict[str, BandFormat]] = None
    output_name_pattern: Optional[str] = "report.html"
    handler: Optional[str] = None  # For custom code
    custom: bool = False

    def get_document_name(self):
        return self.output_name_pattern or "report"


class Parameter(BaseModel):
    name: str  # User friendly name
    alias: str  # for system use
    type: str  # Param Class ?
    # "integer", "string", "date", "model", "choice", "bool", "fields_selector"
    required: bool = False
    default_value: Optional[str] = None
    model_id: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=())

    def clean_value(self, value):
        if self.type == "integer":
            return int(value)
        if self.type == "date":
            return datetime.datetime.strptime(value, "%d.%m.%Y")
        if self.type == "bool":
            return bool(value)
        if self.type == "fields_selector":
            return value.split(",")
        if self.type == "choice":
            return value.split(",")
        if self.type == "model" and self.model_id and value:
            model = get_model(self.model_id)
            if not is_document(model):
                value = int(value)
            value = model.objects.filter(id=value).first()
        return value


@dataclass
class ReportField(object):
    name: str
    output_format: str  # Jinja template


class ReportConfig(BaseModel):
    """
    Report Configuration
    """

    name: str  # Report Name
    root_band: ReportBand  # Report Band (Band Configuration)
    templates: Dict[str, Template]  # Report Templates: template_code -> Template
    parameters: Optional[List[Parameter]] = None  # Report Parameters
    # field_format: Optional[List[ReportField]] = None  # Field Formatter

    def get_root_band(self) -> ReportBand:
        return self.root_band

    def get_template(self, code: str) -> "Template":
        code = code or "DEFAULT"
        try:
            return self.templates[code]
        except KeyError:
            raise ValueError(f"Report template not found for code [{code}]")


class RunParams(BaseModel):
    """
    Report request
    """

    report: ReportConfig
    report_template: Optional[str] = None  # Report Template Code, Use default if not set
    output_type: Optional[OutputType] = None  # Requested OutputType (if not set used from template)
    params: Optional[Dict[str, Any]] = None  # Requested report params
    output_name_pattern: Optional[str] = None  # Output document file name

    def get_template(self) -> "Template":
        return self.report.get_template(self.report_template)

    def get_params(self) -> Dict[str, Any]:
        r = {}
        if self.params:
            r.update(self.params)
        return r


class OutputDocument(BaseModel):
    content: bytes
    document_name: str
    output_type: OutputType

    @property
    def content_type(self):
        """
        application/zip
        :return:
        """
        if self.output_type == OutputType.CSV:
            return "text/csv"
        elif self.output_type == OutputType.XLSX:
            return "application/vnd.ms-excel"
        elif self.output_type == OutputType.PDF:
            return "application/pdf"
        elif self.output_type == OutputType.CSV_ZIP:
            return "application/zip"
        return "application/octet-stream"

    def format_django(self) -> str:
        # CSS
        r = [
            "<head>",
            '<link rel="stylesheet" type="text/css" href="/ui/pkg/django-media/admin/css/base.css"/>',
            '<link rel="stylesheet" type="text/css" href="/ui/web/css/django/main.css"/>',
            '<link rel="stylesheet" type="text/css" href="/ui/pkg/fontawesome/css/font-awesome.min.css"/>',
            '<link rel="stylesheet" type="text/css" href="/ui/web/css/colors.css"/></head><body>',
            '<div id="container"><div id="content" class="colM">"',
        ]
        r += [self.content.decode("utf8")]
        r += ["</div></body></html>"]
        return "\n".join(r)

    def get_content(self, raw: bool = False):
        if raw:
            return self.content
        if self.output_type == OutputType.HTML:
            return self.format_django()
        elif self.output_type == OutputType.CSV_ZIP:
            f = TemporaryFile(mode="w+b")
            f.write(self.content)
            f.seek(0)
            response = BytesIO()
            with ZipFile(response, "w", compression=ZIP_DEFLATED) as zf:
                zf.writestr(f"{self.document_name}.csv", f.read())
                zf.filename = f"{self.document_name}.zip"
                self.document_name += ".zip"
            response.seek(0)
            return response.getvalue()
        return self.content


ReportBand.model_rebuild()
