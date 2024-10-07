# ----------------------------------------------------------------------
# sa.job application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any
from dataclasses import dataclass
from typing import Iterable

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.sa.models.job import Job, JobStatus
from noc.core.translation import ugettext as _

SELECTABLE_CLASS = "job-selectable"
STATUS_COLOR = {
    JobStatus.PENDING.value: "#2c3e50",
    JobStatus.WAITING.value: "#7f8c8d",
    JobStatus.RUNNING.value: "#2980b9",
    JobStatus.SUSPENDED.value: "#7f8c8d",
    JobStatus.SUCCESS.value: "#16a085",
    JobStatus.FAILED.value: "#c0392b",
    JobStatus.WARNING.value: "#d35400",
    JobStatus.CANCELLED.value: "#8e44ad",
}
STATUS_FONT_COLOR = {
    JobStatus.PENDING.value: "#ecf0f1",
    JobStatus.WAITING.value: "#ecf0f1",
    JobStatus.RUNNING.value: "#ecf0f1",
    JobStatus.SUSPENDED.value: "#ecf0f1",
    JobStatus.SUCCESS.value: "#ecf0f1",
    JobStatus.FAILED.value: "#ecf0f1",
    JobStatus.WARNING.value: "#ecf0f1",
    JobStatus.CANCELLED.value: "#ecf0f1",
}


class JobApplication(ExtDocApplication):
    """
    Job application
    """

    title = _("Jobs")
    menu = [_("Jobs")]
    model = Job
    glyph = "truck"
    default_ordering = ["-id"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields, nocustom)
        if isinstance(o, Job):
            r["effective_environment"] = o.effective_environment
        return r

    @view("^(?P<id>[0-9a-f]{24})/viz/$", access="read")
    def view_viz(self, request, id: str):
        job = self.get_object_or_404(Job, id=id)
        return self.get_viz(job)

    @staticmethod
    def get_viz(job: Job) -> dict[str, Any]:
        """
        Generate Viz scheme for job.
        """

        def load_job(j: Job) -> Node:
            node = Node.from_job(j)
            for child in Job.objects.filter(parent=j):
                node.add_child(load_job(child))
            return node

        g: dict[str, Any] = {
            "graphAttributes": {"directed": True, "rankdir": "LR", "label": ""},
            "nodes": [],
            "edges": [],
            "subgraphs": [],
        }
        node = load_job(job)
        node.render(g)
        node.render_edges(g)
        return g


@dataclass
class Node(object):
    id: str
    name: str
    status: JobStatus
    children: "list[Node] | None" = None
    depends_on: list[str] | None = None

    @property
    def status_cls(self) -> str | None:
        """
        Return color for job status.
        """
        return self.status.get_color(self.status.value)

    @classmethod
    def from_job(cls, job: Job) -> "Node":
        """Create node from Job record."""
        return Node(
            id=str(job.id),
            name=job.name,
            status=JobStatus(job.status),
            depends_on=[str(j) for j in job.depends_on] if job.depends_on else None,
        )

    def add_child(self, node: "Node") -> None:
        if self.children is None:
            self.children = []
        self.children.append(node)

    def iter_all(self) -> Iterable["Node"]:
        """
        Iterate all nested nodes.
        """
        yield self
        if self.children is not None:
            for c in self.children:
                yield from c.iter_all()

    @property
    def node_id(self) -> str:
        """Node id"""
        if self.children:
            return f"cluster_{self.id}"
        return f"node_{self.id}"

    def render(self, g: dict[str, Any]) -> None:
        """Render node to graph."""
        color = STATUS_COLOR.get(self.status.value, "black")
        font_color = STATUS_FONT_COLOR.get(self.status.value, "black")
        # Single
        if self.children is None:
            g["nodes"].append(
                {
                    "name": self.node_id,
                    "attributes": {
                        "shape": "box",
                        "style": "rounded,filled",
                        "label": self.name,
                        "id": self.id,
                        "class": SELECTABLE_CLASS,
                        "color": color,
                        "fillcolor": color,
                        "fontcolor": font_color,
                    },
                }
            )
            return
        # Subgraph
        sg: dict[str, Any] = {
            "name": self.node_id,
            "graphAttributes": {
                "label": self.name,
                "style": "rounded,dashed",
                "id": self.id,
                "class": SELECTABLE_CLASS,
                "color": color,
            },
            "nodes": [],
            "edges": [],
            "subgraphs": [],
        }
        g["subgraphs"].append(sg)
        for c in self.children:
            c.render(sg)

    def render_edges(self, g: dict[str, Any]) -> None:
        """Render all nested edges to graph."""
        node_map = {node.id: node for node in self.iter_all()}
        for node in node_map.values():
            if node.depends_on is not None:
                for pre_id in node.depends_on:
                    pre_node = node_map.get(pre_id)
                    if not pre_node:
                        continue
                    g["edges"].append({"tail": pre_node.node_id, "head": node.node_id})
