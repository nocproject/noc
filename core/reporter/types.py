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
    CUSTOM = "custom"
    TABLE = "table"


@dataclass
class ReportField(object):
    name: str
    type: str


@dataclass
class ReportQuery(object):
    name: str
    datasource: Optional[str] = None
    sql: Optional[str] = None
    json: Optional[str] = None
    data: Optional[str] = None
    params: Dict[str, Any] = None
    groovy: Optional[str] = None


@dataclass
class ReportBand(object):
    name: str
    queries: Optional[List[ReportQuery]] = None
    parent: Optional["ReportBand"] = None
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
                children.append(ReportBand(**c))
        self.children = children

    def iter_children(self) -> Iterable["ReportBand"]:
        for c in self.children:
            yield c


@dataclass
class Template(object):
    output_type: OutputType
    code: str = "DEFAULT"  # ReportTemplate.DEFAULT_TEMPLATE_CODE;
    # documentPath: str
    content: Optional[bytes] = None
    output_name_pattern: Optional[str] = "report.html"
    handler: Optional[str] = None  # For custom code
    custom: bool = False


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
    output_format: str


@dataclass
class Report(object):
    name: str
    root_band: ReportBand
    templates: Dict[str, Template]  # template_code -> template
    parameters: List[Parameter]
    field_format: List[ReportField]

    def get_root_band(self) -> ReportBand:
        return self.root_band


@dataclass
class RunParams(object):
    report: Report
    report_template: Template
    output_type: OutputType
    params: Dict[str, Any]
    output_name_pattern: str
