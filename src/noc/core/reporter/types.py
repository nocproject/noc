# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import TemporaryFile
from dataclasses import dataclass
from typing import Any

# Third-party modules
from pydantic import BaseModel, ConfigDict

# NOC modules
from noc.models import get_model, is_document

ROOT_BAND = "Root"
HEADER_BAND = "header"


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
    datasource: str | None = None  # DataSource Name
    query: str | None = None  # DataFrame query
    params: dict[str, Any] = None
    json_data: str | None = None
    transpose: bool = False
    transpose_columns: list[str] | None = None


class BandCondition(BaseModel):
    param: str
    value: str

    def __str__(self) -> str:
        return f"{self.param} == {self.value}"


# ReportBand = ForwardRef("ReportBand")


class ReportBand(BaseModel):
    name: str
    queries: list[ReportQuery] | None = None
    source: str | None = None
    parent: str | None = None  # Parent Band
    orientation: BandOrientation = "H"  # Relevant only for xlsx template
    conditions: list[BandCondition] | None = None
    # children: Optional[List["ReportBand"]] = None

    def __str__(self) -> str:
        return f'ReportBand "{self.name}"'

    def __repr__(self) -> str:
        return (
            f'ReportBand "{self.name}" ('
            f"queries: {len(self.queries) if self.queries is not None else None}, "
            f"source: {self.source}, "
            f"parent: {self.parent}, "
            f"conditions: {len(self.conditions) if self.conditions is not None else None})"
        )

    def is_match(self, params: dict[str, Any]) -> bool:
        if not self.conditions:
            return True
        for c in self.conditions:
            if c.param in params:
                return c.value in params[c.param]
        return True

    # def __init__(self, **data) -> None:
    #     super().__init__(**data)
    #     self.children = self.children or []
    #     for c in self.children:
    #         c.parent = self

    # @property
    # def has_children(self) -> bool:
    #     return bool(self.children)

    # def iter_nester(self) -> Iterable["ReportBand"]:
    #     for c in self.children:
    #         yield c
    #         yield from c.iter_nester()


class ColumnFormat(BaseModel):
    """Format settings for column"""

    name: str
    title: str | None = None
    align: ColumnAlign = ColumnAlign(1)
    format_type: str | None = None
    total: str | None = None  # Calculate summary stat
    total_label: str = "Total"


class BandFormat(BaseModel):
    """Configuration for autogenerate template"""

    title_template: str | None = None  # Title format for Section row
    columns: list[ColumnFormat] | None = None  # ColumnName -> ColumnFormat

    def __str__(self) -> str:
        return f'BandFormat "{self.title_template}"'

    def __repr__(self) -> str:
        return (
            f'BandFormat "{self.title_template}" ('
            f"title_template: {self.title_template}, "
            f"columns: {len(self.columns) if self.columns is not None else None})"
        )


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
    content: bytes | None = None
    formatter: str | None = None
    bands_format: dict[str, BandFormat] | None = None
    output_name_pattern: str | None = "report.html"
    handler: str | None = None  # For custom code
    custom: bool = False

    def get_document_name(self):
        return self.output_name_pattern or "report"

    def __str__(self) -> str:
        return f'Template "{self.code}"'

    def __repr__(self) -> str:
        return (
            f'Template "{self.code}" (output_type: {self.output_type}, '
            f"content: {self.content}, "
            f"formatter: {self.formatter}, "
            f"bands_format: {len(self.bands_format) if self.bands_format is not None else None})"
        )


class Parameter(BaseModel):
    name: str  # User friendly name
    type: str  # Param Class ?
    # "integer", "string", "date", "model", "choice", "bool", "fields_selector"
    required: bool = False
    alias: str | None = None  # for system use
    default_value: str | None = None
    model_id: str | None = None

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
class ReportField:
    name: str
    output_format: str  # Jinja template


class ReportConfig(BaseModel):
    """
    Report Configuration
    """

    name: str  # Report Name
    bands: list[ReportBand]  # Report Band (Band Configuration)
    templates: dict[str, Template]  # Report Templates: template_code -> Template
    parameters: list[Parameter] | None = None  # Report Parameters
    align_end_date_param: bool = False
    # field_format: Optional[List[ReportField]] = None  # Field Formatter

    def __str__(self) -> str:
        return f'ReportConfig "{self.name}"'

    def __repr__(self) -> str:
        return (
            f'ReportConfig "{self.name}" ('
            f"bands: {len(self.bands)}, "
            f"templates: {len(self.templates)}, "
            f"parameters: {len(self.parameters) if self.parameters is not None else None})"
        )

    def get_root_band(self) -> ReportBand:
        return next(b for b in self.bands if b.name == ROOT_BAND)

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

    report_config: ReportConfig
    report_template: str | None = None  # Report Template Code, Use default if not set
    output_type: OutputType | None = None  # Requested OutputType (if not set used from template)
    params: dict[str, Any] | None = None  # Requested report params
    output_name_pattern: str | None = None  # Output document file name

    def __str__(self) -> str:
        return f'RunParams "{self.report_config.name}"'

    def __repr__(self) -> str:
        return (
            f'RunParams "{self.report_config.name}" ('
            f"report_config: {self.report_config}, "
            f"report_template: {self.report_template}, "
            f"output_type: {self.output_type}, "
            f"params: {len(self.params) if self.params is not None else None})"
        )

    def get_template(self) -> Template:
        return self.report_config.get_template(self.report_template)

    def get_params(self) -> dict[str, Any]:
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
        if self.output_type == OutputType.XLSX:
            return "application/vnd.ms-excel"
        if self.output_type == OutputType.PDF:
            return "application/pdf"
        if self.output_type == OutputType.CSV_ZIP:
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
        r.append(self.content.decode("utf8"))
        r.append("</div></body></html>")
        return "\n".join(r)

    def get_content(self, raw: bool = False):
        if raw:
            return self.content
        if self.output_type == OutputType.HTML:
            return self.format_django()
        if self.output_type == OutputType.CSV_ZIP:
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
