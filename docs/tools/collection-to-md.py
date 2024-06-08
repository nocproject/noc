# ----------------------------------------------------------------------
# Fill .md from collections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import json
import os
from typing import Dict, DefaultDict, Any, Iterable, List, Optional
from dataclasses import dataclass
import enum
import re
import shutil
import operator
from collections import defaultdict


def quote_file_name(s: str) -> str:
    return s.strip().lower().replace(" ", "-").replace(":", "").replace("/", "-")


def mq(s: str) -> str:
    return s.replace("|", r"\|")


def rel_ref(from_path: str, to_path: str) -> str:
    """
    Calculate related reference
    :param from_path:
    :param to_path:
    :return:
    """
    path1 = from_path.split("/")[:-1]
    path2 = to_path.split("/")
    fn = path2.pop(-1)
    common = 0
    for x, y in zip(path1, path2):
        if x != y:
            break
        common += 1
    parts = []
    up = len(path1) - common
    if up:
        parts += [".."] * up
    down = len(path2) - common
    if down:
        parts += path2[common:]
    parts += [fn]
    return "/".join(parts)


@dataclass
class EventClassVar(object):
    name: str
    description: str
    type: str
    is_required: bool

    @property
    def is_required_mark(self):
        if self.is_required:
            return "{{ yes }}"
        else:
            return "{{ no }}"


class DispositionAction(enum.Enum):
    CLEAR = "clear"
    RAISE = "raise"
    IGNORE = "ignore"


@dataclass
class EventClassDisposition(object):
    name: str
    action: DispositionAction
    alarm: str


@dataclass
class EventClass(object):
    name: str
    uuid: str
    description: str
    symptoms: str
    probable_causes: str
    recommended_actions: str
    vars: Optional[List[EventClassVar]]
    disposition: Optional[List[EventClassDisposition]]

    @property
    def dir_path(self) -> List[str]:
        return [quote_file_name(x) for x in self.name.split(" | ")][:-1]

    @property
    def file_name(self) -> str:
        return quote_file_name(self.name.split(" | ")[-1]) + ".md"

    @property
    def rel_path(self) -> str:
        return f"reference/event-classes/{'/'.join(self.dir_path)}/{self.file_name}"


@dataclass
class AlarmClassVar(object):
    name: str
    description: str
    default: Optional[str]

    @property
    def default_mark(self) -> str:
        if self.default:
            return f"`{self.default}`"
        return "{{ no }}"


@dataclass
class RoutCause(object):
    name: str
    alarm_class: str


@dataclass
class AlarmEvent(object):
    event_class: str
    name: str


@dataclass
class AlarmClass(object):
    name: str
    uuid: str
    description: str
    symptoms: str
    probable_causes: str
    recommended_actions: str
    vars: Optional[List[AlarmClassVar]]
    root_causes: Optional[List[RoutCause]]
    consequences: Optional[List[RoutCause]]
    opening_events: Optional[List[AlarmEvent]]
    closing_events: Optional[List[AlarmEvent]]

    @property
    def dir_path(self) -> List[str]:
        return [quote_file_name(x) for x in self.name.split(" | ")][:-1]

    @property
    def file_name(self) -> str:
        return quote_file_name(self.name.split(" | ")[-1]) + ".md"

    @property
    def rel_path(self) -> str:
        return f"reference/alarm-classes/{'/'.join(self.dir_path)}/{self.file_name}"


@dataclass
class MetricScopePath(object):
    name: str
    is_required: bool

    @property
    def is_required_mark(self):
        if self.is_required:
            return "{{ yes }}"
        else:
            return "{{ no }}"


@dataclass
class MetricScope(object):
    name: str
    uuid: str
    table_name: str
    description: Optional[str]
    path: List[MetricScopePath]
    metric_types: List["MetricType"]

    @property
    def file_name(self) -> str:
        return quote_file_name(self.name) + ".md"

    @property
    def rel_path(self) -> str:
        return f"reference/metrics/scopes/{self.file_name}"


@dataclass
class MetricType(object):
    name: str
    uuid: str
    scope: MetricScope
    field_name: str
    field_type: str
    description: Optional[str]
    measure: str

    @property
    def dir_path(self) -> List[str]:
        return [quote_file_name(x) for x in self.name.split(" | ")][:-1]

    @property
    def file_name(self) -> str:
        return quote_file_name(self.name.split(" | ")[-1]) + ".md"

    @property
    def rel_path(self) -> str:
        return f"reference/metrics/types/{'/'.join(self.dir_path)}/{self.file_name}"


@dataclass
class AltMeasurementUnits(object):
    name: str
    description: Optional[str]
    label: str
    dashboard_label: str
    from_primary: str
    to_primary: str


@dataclass
class MeasurementUnits(object):
    name: str
    uuid: str
    description: Optional[str]
    label: str
    dashboard_label: str
    scale_type: str
    alt_units: Optional[List[AltMeasurementUnits]]

    @property
    def file_name(self) -> str:
        return quote_file_name(self.name) + ".md"

    @property
    def rel_path(self) -> str:
        return f"reference/measurement-units/{self.file_name}"


@dataclass
class ConnectionType(object):
    name: str
    uuid: str
    description: Optional[str]
    extend: Optional[str]
    genders: str
    c_group: Optional[List[str]]

    @property
    def dir_path(self) -> List[str]:
        return [quote_file_name(x) for x in self.name.split(" | ")][:-1]

    @property
    def file_name(self) -> str:
        return quote_file_name(self.name.split(" | ")[-1]) + ".md"

    @property
    def rel_path(self) -> str:
        return f"reference/connection-type/{'/'.join(self.dir_path)}/{self.file_name}"


GENDER_DESC = {
    "s": "symmetric, genderless same type connection",
    "ss": "symmetric, genderless same type connection. More than two objects may be connected",
    "m": "only male types, compatible female types are selected via `c_groups`",
    "f": "only female types, compatible male types are selected via `c_groups`",
    "mf": "male and female types",
    "mmf": "one or more male may be connected to one female",
    "mff": "two or one females may be connected to one male",
}


class FileWriter(object):
    def __init__(self, root: str):
        self.root = root
        self.new_files = 0
        self.changed_files = 0
        self.unmodified_files = 0

    def write(self, path: str, data: List[str]):
        path = os.path.join(self.root, path)
        # Ensure directory
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Add line break to the end of file, when necessary
        if data and data[-1]:
            data += [""]
        # Check if page modified
        page = "\n".join(data)
        to_write = False
        if os.path.exists(path):
            with open(path) as f:
                old_page = f.read()
            if old_page == page:
                self.unmodified_files += 1
            else:
                self.changed_files += 1
                to_write = 1
        else:
            self.new_files += 1
            to_write = True
        if to_write:
            print(f"  Writing: {path}")
            with open(path, "w") as f:
                f.write(page)

    def summary(self):
        total_files = self.new_files + self.changed_files + self.unmodified_files
        print(
            f"  Pages: new {self.new_files}, changed {self.changed_files}, unmodified {self.unmodified_files}, total {total_files}"
        )


class CollectionDoc(object):
    rx_indent = re.compile(r"^(\s+)-")

    def __init__(self):
        full_path = os.path.abspath(sys.argv[0])
        self.src_root = os.path.abspath(os.path.join(os.path.dirname(full_path), "..", ".."))
        self.doc_root = os.path.join(self.src_root, "docs", "en", "docs")
        self.yml_path = os.path.join(self.src_root, "docs", "en", "mkdocs.yml")
        self.new_yml_path = f"{self.yml_path}.new"
        self.event_class: Dict[str, EventClass] = {}
        self.alarm_class: Dict[str, AlarmClass] = {}
        self.metric_scope: Dict[str, MetricScope] = {}
        self.metric_type: Dict[str, MetricType] = {}
        self.measurement_units: Dict[str, MeasurementUnits] = {}
        self.connection_types: Dict[str, ConnectionType] = {}
        self.c_groups: DefaultDict[str, List[str]] = defaultdict(list)

    def build(self):
        shutil.copy(self.yml_path, self.new_yml_path)
        self.read_collections()
        self.build_eventclasses()
        self.build_alarmclasses()
        self.build_metric_scopes()
        self.build_metric_types()
        self.build_measurement_units()
        self.build_connection_types()

    def read_collections(self):
        self.read_eventclasses()
        self.read_alarmclasses()
        self.read_metric_scopes()
        self.read_metric_types()
        self.read_measurement_units()
        self.read_connection_types()

    def iter_jsons(self, path: str) -> Iterable[Dict[str, Any]]:
        for root, _, files in os.walk(path):
            for fn in files:
                if fn.startswith(".") or not fn.endswith(".json"):
                    continue
                with open(os.path.join(root, fn)) as f:
                    yield json.loads(f.read())

    def read_eventclasses(self):
        for d in self.iter_jsons(os.path.join("collections", "fm.eventclasses")):
            event_class = EventClass(
                name=d["name"],
                uuid=d["uuid"],
                description=d.get("description") or "",
                symptoms=d.get("symptoms") or "",
                probable_causes=d.get("probable_causes") or "",
                recommended_actions=d.get("recommended_actions") or "",
                vars=None,
                disposition=None,
            )
            ec_vars = d.get("vars")
            if ec_vars:
                event_class.vars = [
                    EventClassVar(
                        name=v["name"],
                        description=v["description"],
                        type=v.get("type"),
                        is_required=bool(v.get("required")),
                    )
                    for v in ec_vars
                ]
            ec_disposition = d.get("disposition")
            if ec_disposition:
                event_class.disposition = [
                    EventClassDisposition(
                        name=v["name"],
                        action=DispositionAction(v["action"]),
                        alarm=v["alarm_class__name"],
                    )
                    for v in ec_disposition
                    if v["action"] != "ignore"
                ]
            self.event_class[event_class.name] = event_class

    def read_alarmclasses(self):
        for d in self.iter_jsons(os.path.join("collections", "fm.alarmclasses")):
            alarm_class = AlarmClass(
                name=d["name"],
                uuid=d["uuid"],
                description=d.get("description") or "",
                symptoms=d.get("symptoms") or "",
                probable_causes=d.get("probable_causes") or "",
                recommended_actions=d.get("recommended_actions") or "",
                vars=None,
                root_causes=None,
                consequences=None,
                opening_events=None,
                closing_events=None,
            )
            ac_vars = d.get("vars")
            if ac_vars:
                alarm_class.vars = [
                    AlarmClassVar(
                        name=v["name"],
                        description=v["description"],
                        default=v.get("default"),
                    )
                    for v in ac_vars
                ]
            root_causes = d.get("root_cause")
            if root_causes:
                alarm_class.root_causes = [
                    RoutCause(
                        name=v["name"],
                        alarm_class=v["root__name"],
                    )
                    for v in root_causes
                ]
            self.alarm_class[alarm_class.name] = alarm_class
        # Connect consequences
        for ac in self.alarm_class.values():
            if not ac.root_causes:
                continue
            for rc in ac.root_causes:
                rcls = self.alarm_class[rc.alarm_class]
                if rcls.consequences is None:
                    rcls.consequences = []
                rcls.consequences += [RoutCause(name=rc.name, alarm_class=ac.name)]
        # Connect events
        for ec in self.event_class.values():
            if not ec.disposition:
                continue
            for ed in ec.disposition:
                ac = self.alarm_class[ed.alarm]
                if ed.action == DispositionAction.RAISE:
                    if ac.opening_events is None:
                        ac.opening_events = []
                    ac.opening_events += [AlarmEvent(event_class=ec.name, name=ed.name)]
                elif ed.action == DispositionAction.CLEAR:
                    if ac.closing_events is None:
                        ac.closing_events = []
                    ac.closing_events += [AlarmEvent(event_class=ec.name, name=ed.name)]
                else:
                    raise ValueError(f"Unknown disposition: {ed.action}")

    def read_metric_scopes(self):
        for d in self.iter_jsons(os.path.join("collections", "pm.metricscopes")):
            metric_scope = MetricScope(
                name=d["name"],
                uuid=d["uuid"],
                path=[],
                description=d.get("description") or "",
                table_name=d["table_name"],
                metric_types=[],
            )
            path = d.get("path") or []
            for p in path:
                metric_scope.path += [
                    MetricScopePath(name=p["name"], is_required=bool(p.get("is_required")))
                ]
            self.metric_scope[metric_scope.name] = metric_scope

    def read_metric_types(self):
        for d in self.iter_jsons(os.path.join("collections", "pm.metrictypes")):
            metric_scope = self.metric_scope[d["scope__name"]]
            metric_type = MetricType(
                name=d["name"],
                uuid=d["uuid"],
                scope=metric_scope,
                description=d.get("description") or "",
                field_name=d["field_name"],
                field_type=d["field_type"],
                measure=d.get("measure") or "",
            )
            self.metric_type[metric_type.name] = metric_type
            metric_scope.metric_types += [metric_type]

    def read_measurement_units(self):
        for d in self.iter_jsons(os.path.join("collections", "pm.measurementunits")):
            unit = MeasurementUnits(
                name=d["name"],
                uuid=d["uuid"],
                description=d.get("description") or "",
                label=d["label"],
                dashboard_label=d["dashboard_label"],
                scale_type=d["scale_type"],
                alt_units=[
                    AltMeasurementUnits(
                        name=a["name"],
                        description=a.get("description") or "",
                        label=a["label"],
                        dashboard_label=a["dashboard_label"],
                        from_primary=a.get("from_primary") or "",
                        to_primary=a.get("to_primary") or "",
                    )
                    for a in d.get("alt_units") or []
                ],
            )
            self.measurement_units[unit.name] = unit

    def read_connection_types(self):
        for d in self.iter_jsons(os.path.join("collections", "inv.connectiontypes")):
            ct = ConnectionType(
                name=d["name"],
                uuid=d["uuid"],
                description=d.get("description") or "",
                extend=d.get("extend") or None,
                genders=d.get("genders") or "mf",
                c_group=d.get("c_group") or None,
            )
            self.connection_types[ct.name] = ct
            if ct.c_group:
                for c_group in ct.c_group:
                    self.c_groups[c_group] += [ct.name]

    def update_toc(self, key: str, lines: List[str]):
        r = []
        rx_key = re.compile(rf"^(\s+)- {key}:")
        indent = ""
        to_feed = False
        with open(self.new_yml_path) as f:
            for line in f:
                line = line[:-1]
                if to_feed:
                    # Feed rest of ToC
                    r += [line]
                    continue
                if not indent:
                    # Search mode
                    r += [line]
                    match = rx_key.search(line)
                    if match:
                        indent = match.group(1)
                        # Inject new part of ToC
                        r += [f"{indent}    {item}" for item in lines]
                    continue
                # Search for the next item
                match = self.rx_indent.search(line)
                if match:
                    if len(match.group(1)) <= len(indent):
                        to_feed = True
                    else:
                        continue  # Skip replaced part
                r += [line]
        r += [""]
        with open(self.new_yml_path, "w") as f:
            f.write("\n".join(r))

    def build_eventclasses(self):
        print("# Writing event classes doc:")
        toc = ["- Overview: event-classes-reference/index.md"]
        writer = FileWriter(os.path.join(self.doc_root, "user", "reference", "event-classes"))
        last_path: List[str] = []
        indent: str = ""
        for ec_name in sorted(self.event_class):
            ec = self.event_class[ec_name]
            rel_dir = os.path.join(*ec.dir_path)
            path = [x.strip() for x in ec_name.split(" | ")][:-1]
            if not last_path or path != last_path:
                level = 0
                for last_pc, current_pc in zip(last_path, path):
                    if last_pc == current_pc:
                        level += 1
                    else:
                        break
                indent = "    " * (level - 1)
                for current_pc in path[level:]:
                    indent = "    " * level
                    toc += [f'{indent}- "{current_pc}":']
                    level += 1
                last_path = path
            short_name = ec_name.split(" | ")[-1].strip()
            toc += [
                f'{indent}    - "{short_name}": event-classes-reference/{rel_dir}/{ec.file_name}'
            ]
            # render page
            data = ["---", f"uuid: {ec.uuid}", "---", f"# {ec.name}"]
            if ec.description:
                data += ["", ec.description]
            data += ["", "## Symptoms"]
            if ec.symptoms:
                data += ["", ec.symptoms]
            data += ["", "## Probable Causes"]
            if ec.probable_causes:
                data += ["", ec.probable_causes]
            data += ["", "## Recommended Actions"]
            if ec.recommended_actions:
                data += ["", ec.recommended_actions]
            if ec.vars:
                data += [
                    "",
                    "## Variables",
                    "",
                    "Variable | Type | Required | Description",
                    "--- | --- | --- | ---",
                ]
                data += [
                    f"{v.name} | {v.type} | {v.is_required_mark} | {v.description}" for v in ec.vars
                ]
            if ec.disposition:
                data += ["", "## Alarms"]
                d_list = [d for d in ec.disposition if d.action == DispositionAction.RAISE]
                if d_list:
                    data += [
                        "",
                        "### Raising alarms",
                        "",
                        f"`{ec.name}` events may raise following alarms:",
                        "",
                        "Alarm Class | Description",
                        "--- | ---",
                    ]
                    for d in d_list:
                        alarm_ref = rel_ref(ec.rel_path, self.alarm_class[d.alarm].rel_path)
                        data += [f"[{mq(d.alarm)}]({alarm_ref}) | {d.name}"]
                d_list = [d for d in ec.disposition if d.action == DispositionAction.CLEAR]
                if d_list:
                    data += [
                        "",
                        "### Clearing alarms",
                        "",
                        f"`{ec.name}` events may clear following alarms:",
                        "",
                        "Alarm Class | Description",
                        "--- | ---",
                    ]
                    for d in d_list:
                        alarm_ref = rel_ref(ec.rel_path, self.alarm_class[d.alarm].rel_path)
                        data += [f"[{mq(d.alarm)}]({alarm_ref}) | {d.name}"]
            writer.write(os.path.join(rel_dir, ec.file_name), data)
        writer.summary()
        self.update_toc("Event Classes", toc)

    def build_alarmclasses(self):
        print("# Writing alarm classes doc:")
        toc = ["- Overview: alarm-classes-reference/index.md"]
        writer = FileWriter(os.path.join(self.doc_root, "user", "reference", "alarm-classes"))
        last_path: List[str] = []
        indent: str = ""
        for ac_name in sorted(self.alarm_class):
            ac = self.alarm_class[ac_name]
            rel_dir = os.path.join(*ac.dir_path)
            path = [x.strip() for x in ac_name.split(" | ")][:-1]
            if not last_path or path != last_path:
                level = 0
                for last_pc, current_pc in zip(last_path, path):
                    if last_pc == current_pc:
                        level += 1
                    else:
                        break
                indent = "    " * (level - 1)
                for current_pc in path[level:]:
                    indent = "    " * level
                    toc += [f'{indent}- "{current_pc}":']
                    level += 1
                last_path = path
            short_name = ac_name.split(" | ")[-1].strip()
            toc += [
                f'{indent}    - "{short_name}": alarm-classes-reference/{rel_dir}/{ac.file_name}'
            ]
            # render page
            data = ["---", f"uuid: {ac.uuid}", "---", f"# {ac.name}"]
            if ac.description:
                data += ["", ac.description]
            data += ["", "## Symptoms"]
            if ac.symptoms:
                data += ["", ac.symptoms]
            data += ["", "## Probable Causes"]
            if ac.probable_causes:
                data += ["", ac.probable_causes]
            data += ["", "## Recommended Actions"]
            if ac.recommended_actions:
                data += ["", ac.recommended_actions]
            if ac.vars:
                data += [
                    "",
                    "## Variables",
                    "",
                    "Variable | Description | Default",
                    "--- | --- | ---",
                ]
                data += [f"{v.name} | {v.description} | {v.default_mark}" for v in ac.vars]
            if ac.root_causes or ac.consequences:
                # Build scheme
                data += [
                    "",
                    "## Alarm Correlation",
                    "",
                    f"Scheme of correlation of `{ac.name}` alarms with other alarms is on the chart. ",
                    "Arrows are directed from root cause to consequences.",
                    "",
                    "```mermaid",
                    "graph TD",
                ]
                defs = [f'  A[["{ac.name}"]]']
                body = []
                if ac.root_causes:
                    for rc in ac.root_causes:
                        c_name = f"R{len(defs)}"
                        defs += [f'  {c_name}["{rc.alarm_class}"]']
                        body += [f"  {c_name} --> A"]
                if ac.consequences:
                    for rc in ac.consequences:
                        c_name = f"C{len(defs)}"
                        defs += [f'  {c_name}["{rc.alarm_class}"]']
                        body += [f"  A --> {c_name}"]
                data += defs
                data += body
                data += ["```"]
            if ac.root_causes:
                data += [
                    "",
                    "### Root Causes",
                    f"`{ac.name}` alarm may be consequence of",
                    "",
                    "Alarm Class | Description",
                    "--- | ---",
                ]
                for rc in ac.root_causes:
                    a_ref = rel_ref(ac.rel_path, self.alarm_class[rc.alarm_class].rel_path)
                    data += [f"[{mq(rc.alarm_class)}]({a_ref}) | {rc.name}"]
            if ac.consequences:
                data += [
                    "",
                    "### Consequences",
                    f"`{ac.name}` alarm may be root cause of",
                    "",
                    "Alarm Class | Description",
                    "--- | ---",
                ]
                for rc in ac.consequences:
                    a_ref = rel_ref(ac.rel_path, self.alarm_class[rc.alarm_class].rel_path)
                    data += [f"[{mq(rc.alarm_class)}]({a_ref}) | {rc.name}"]
            if ac.opening_events or ac.closing_events:
                data += ["", "## Events"]
            if ac.opening_events:
                data += [
                    "",
                    "### Opening Events",
                    f"`{ac.name}` may be raised by events",
                    "",
                    "Event Class | Description",
                    "--- | ---",
                ]
                for e in ac.opening_events:
                    e_ref = rel_ref(ac.rel_path, self.event_class[e.event_class].rel_path)
                    data += [f"[{mq(e.event_class)}]({e_ref}) | {e.name}"]
            if ac.closing_events:
                data += [
                    "",
                    "### Closing Events",
                    f"`{ac.name}` may be cleared by events",
                    "",
                    "Event Class | Description",
                    "--- | ---",
                ]
                for e in ac.closing_events:
                    e_ref = rel_ref(ac.rel_path, self.event_class[e.event_class].rel_path)
                    data += [f"[{mq(e.event_class)}]({e_ref}) | {e.name}"]
            writer.write(os.path.join(rel_dir, ac.file_name), data)
        writer.summary()
        self.update_toc("Alarm Classes", toc)

    def build_metric_scopes(self):
        print("# Writing metric scopes doc:")
        writer = FileWriter(os.path.join(self.doc_root, "user", "reference", "metrics", "scopes"))
        tab = "{{ tab }}"
        toc = ["- Overview: metric-scopes-reference/index.md"]
        for ms_name in sorted(self.metric_scope):
            ms = self.metric_scope[ms_name]
            data = ["---", f"uuid: {ms.uuid}", "---", f"# {ms.name} Metric Scope"]
            if ms.description:
                data += ["", ms.description]
            data += [
                "",
                "## Data Table",
                "",
                f"ClickHouse Table: `{ms.table_name}`",
                "",
                "Field | Type | Description",
                "--- | --- | ---",
                "date | Date | Measurement Date",
                "ts | DateTime | Measurement Timestamp",
            ]
            if ms.path:
                data += [
                    "path | Array of String {{ complex }} | Measurement Path",
                ]
                data += [f"{tab} `{p.name}` | {p.is_required_mark} | " for p in ms.path]
            for mt in sorted(ms.metric_types, key=operator.attrgetter("field_name")):
                mt_ref = rel_ref(ms.rel_path, mt.rel_path)
                data += [
                    f"[{mt.field_name}]({mt_ref}) | {mt.field_type} | [{mq(mt.name)}]({mt_ref})"
                ]
            data += [""]
            toc += [f"- {ms.name}: metric-scopes-reference/{ms.file_name}"]
            writer.write(ms.file_name, data)
        writer.summary()
        self.update_toc("Metric Scopes", toc)

    def build_metric_types(self):
        print("# Writing metric types doc:")
        writer = FileWriter(os.path.join(self.doc_root, "user", "reference", "metrics", "types"))
        last_path: List[str] = []
        indent: str = ""
        toc = ["- Overview: metric-types-reference/index.md"]
        for mt_name in sorted(self.metric_type):
            mt = self.metric_type[mt_name]
            rel_dir = os.path.join(*mt.dir_path)
            path = [x.strip() for x in mt_name.split(" | ")][:-1]
            if not last_path or path != last_path:
                level = 0
                for last_pc, current_pc in zip(last_path, path):
                    if last_pc == current_pc:
                        level += 1
                    else:
                        break
                indent = "    " * (level - 1)
                for current_pc in path[level:]:
                    indent = "    " * level
                    toc += [f'{indent}- "{current_pc}":']
                    level += 1
                last_path = path
            short_name = mt_name.split(" | ")[-1].strip()
            toc += [
                f'{indent}    - "{short_name}": metric-types-reference/{rel_dir}/{mt.file_name}'
            ]
            # Render page
            data = ["---", f"uuid: {mt.uuid}", "---", f"# {mt.name} Metric Type"]
            if mt.description:
                data += ["", mt.description]
            scope_path = rel_ref(mt.rel_path, mt.scope.rel_path)
            data += [
                "",
                "## Data Model",
                "",
                "Scope",
                f": [{mt.scope.name}]({scope_path})",
                "",
                "Field",
                f": `{mt.field_name}`",
                "",
                "Type",
                f": {mt.field_type}",
                "",
                "Measure",
                f": `{mt.measure}`",
                "",
            ]
            writer.write(os.path.join(rel_dir, mt.file_name), data)
        writer.summary()
        self.update_toc("Metric Types", toc)

    def build_measurement_units(self) -> None:
        print("# Writing measurement units doc:")
        writer = FileWriter(os.path.join(self.doc_root, "user", "reference", "measurement-units"))
        toc = ["- Overview: measurement-units-reference/index.md"]
        for mu_name in sorted(self.measurement_units):
            mu = self.measurement_units[mu_name]
            data = ["---", f"uuid: {mu.uuid}", "---", f"# {mu.name} Measurement Units"]
            if mu.description:
                data += ["", mu.description]
            scale = {"d": "Decimal", "b": "Binary"}[mu.scale_type]
            data += [
                "",
                "Scale",
                f": {scale}",
                "",
                "Label",
                f": `{mu.label}`",
                "",
                "Dashboard Label",
                f": `{mu.dashboard_label}`",
            ]
            if mu.alt_units:
                data += [
                    "",
                    "## Alternative Units",
                    "",
                    "Name | Description | Label | Dash. Label | From Primary | To Primary",
                    "--- | --- | --- | --- | --- | ---",
                ]
                data += [
                    f"{a.name} | {a.description} | {a.label} | {a.dashboard_label} | `{a.from_primary}` | `{a.to_primary}`"
                    for a in mu.alt_units
                ]
            data += [""]
            toc += [f"- {mu.name}: measurement-units-reference/{mu.file_name}"]
            writer.write(mu.file_name, data)
        writer.summary()
        self.update_toc("Measurement Units", toc)

    def build_connection_types(self):
        print("# Writing connection types doc:")
        writer = FileWriter(os.path.join(self.doc_root, "dev", "reference", "connection-type"))
        last_path: List[str] = []
        indent: str = ""
        toc = ["- Overview: connection-types-reference/index.md"]
        for ct_name in sorted(self.connection_types):
            ct = self.connection_types[ct_name]
            dir_path = ct.dir_path
            rel_dir = os.path.join(*ct.dir_path) if dir_path else ""
            path = [x.strip() for x in ct_name.split(" | ")][:-1]
            if not last_path or path != last_path:
                level = 0
                for last_pc, current_pc in zip(last_path, path):
                    if last_pc == current_pc:
                        level += 1
                    else:
                        break
                indent = "    " * (level - 1)
                for current_pc in path[level:]:
                    indent = "    " * level
                    toc += [f'{indent}- "{current_pc}":']
                    level += 1
                last_path = path
            short_name = ct_name.split(" | ")[-1].strip()
            toc += [
                f'{indent}    - "{short_name}": connection-types-reference/{rel_dir}/{ct.file_name}'
            ]
            # Render page
            data = ["---", f"uuid: {ct.uuid}", "---", f"# {ct.name} Connection Type"]
            if ct.description:
                data += ["", ct.description]
            if ct.extend:
                data += ["", "Extends", f": {ct.extend}"]
            data += ["", "Genders", f": `{ct.genders}` - {GENDER_DESC[ct.genders]}"]
            if ct.c_group:
                data += ["", "CGroups"]
                for n, c_group in enumerate(sorted(ct.c_group)):
                    if n:
                        data += [f"    - {c_group}:", ""]
                    else:
                        data += [f":   - {c_group}:", ""]
                    for name in sorted(self.c_groups[c_group]):
                        rel = rel_ref(ct.rel_path, self.connection_types[name].rel_path)
                        data += [f"        - [{name}]({rel})"]
                    data += [""]
            writer.write(os.path.join(rel_dir, ct.file_name), data)
        writer.summary()
        self.update_toc("Connection Types", toc)


if __name__ == "__main__":
    CollectionDoc().build()
