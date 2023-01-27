from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import enum


class BandOrientation(enum.StrEnum):
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
class ReportBand(object):
    name: str
    orientation: BandOrientation = "H"  # Relevant only for xlsx template
    children: List["ReportBand"] = field(default_factory=list)
    query: List[str] = field(default_factory=list)  # datasources
    parent: Optional["ReportBand"] = None


@dataclass
class Template(object):
    output_type: OutputType
    code: str = "DEFAULT" # ReportTemplate.DEFAULT_TEMPLATE_CODE;
    # documentPath: str
    content: Optional[bytes] = None
    output_name_pattern: Optional[str] = "report.html"
    handler: Optional[str] = None # For custom code
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
    # field_format: List[ReportField]


@dataclass
class RunParams(object):
    report: Report
    report_template: Template
    output_type: OutputType
    params: Dict[str, Any]
    output_name_pattern: str
