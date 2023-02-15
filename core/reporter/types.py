# ----------------------------------------------------------------------
# Report Engine Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Iterable


class BandOrientation(enum.Enum):
    HORIZONTAL = "H"
    VERTICAL = "V"
    CROSS = "C"
    UNDEFINED = "U"


class OutputType(enum.Enum):
    HTML = "html"
    XLSX = "xlsx"
    CSV = "csv"
    SSV = "ssv"
    PDF = "pdf"


class ColumnAlign(enum.Enum):
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    MASK = 3


@dataclass
class ReportField(object):
    name: str
    type: str


@dataclass
class ReportQuery(object):
    name: str
    datasource: Optional[str] = None  # DataSource Name
    query: Optional[str] = None  # DataFrame query
    fields: Optional[List[str]] = None  # DataSource Fields for query
    params: Dict[str, Any] = None
    json: Optional[str] = None


@dataclass
class ReportBand(object):
    name: str
    title_template: Optional[str] = None  # Title format for Section row
    queries: Optional[List[ReportQuery]] = None
    parent: Optional["ReportBand"] = None  # Parent Band
    orientation: BandOrientation = "H"  # Relevant only for xlsx template
    children: Optional[List["ReportBand"]] = None

    def __post_init__(self):
        queries = []
        for q in self.queries or []:
            if isinstance(q, dict):
                queries.append(ReportQuery(**q))
        self.queries = queries
        children = []
        for c in self.children or []:
            if isinstance(c, dict):
                c["parent"] = self
                children.append(ReportBand(**c))
        self.children = children

    def iter_nester(self) -> Iterable["ReportBand"]:
        for c in self.children:
            yield c
            yield from c.children


@dataclass
class ColumnFormat(object):
    title: Optional[str] = None
    align: ColumnAlign = ColumnAlign.LEFT
    format_type: Optional[str] = None
    has_total: bool = False  # Calculate summary stat


@dataclass
class Template(object):
    output_type: OutputType
    code: str = "DEFAULT"  # ReportTemplate.DEFAULT_TEMPLATE_CODE;
    # documentPath: str
    content: Optional[bytes] = None
    formatter: Optional[str] = None  # Formatter name. Or Autodetect by content
    columns_format: Optional[
        Dict[str, ColumnFormat]
    ] = None  # BandName -> ColumnName -> ColumnFormat
    output_name_pattern: Optional[str] = "report.html"
    handler: Optional[str] = None  # For custom code
    custom: bool = False

    def get_document_name(self):
        return self.output_name_pattern

    def __post_init__(self):
        if not isinstance(self.output_type, OutputType):
            self.output_type = OutputType(self.output_type)
        if not self.columns_format:
            return
        for c_name in list(self.columns_format):
            self.columns_format[c_name] = ColumnFormat(**self.columns_format[c_name])


@dataclass
class Parameter(object):
    name: str  # User friendly name
    alias: str  # for system use
    type: str  # Param Class ?
    required: bool = False
    default_value: Optional[str] = None


@dataclass
class ReportField(object):
    name: str
    output_format: str  # Jinja template


@dataclass
class Report(object):
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

    def __post_init__(self):
        if isinstance(self.root_band, dict):
            self.root_band = ReportBand(**self.root_band)
        for code, t in self.templates.items():
            if isinstance(t, dict):
                self.templates[code] = Template(**t)


@dataclass
class RunParams(object):
    """
    Report request
    """

    report: Report
    report_template: Optional[str] = None  # Report Template Code, Use default if not set
    output_type: Optional[OutputType] = None  # Requested OutputType (if not set used from template)
    params: Optional[Dict[str, Any]] = None  # Requested report params
    output_name_pattern: Optional[str] = None  # Output document file name

    def get_template(self) -> "Template":
        return self.report.get_template(self.report_template)

    def get_params(self) -> Dict[str, Any]:
        r = {}
        if self.report.parameters:
            r.update(self.report.parameters)
        if self.params:
            r.update(self.params)
        return r
