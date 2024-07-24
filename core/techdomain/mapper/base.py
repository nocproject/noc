# ----------------------------------------------------------------------
# BaseMapper class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import List, Iterable, Optional

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.inv.models.channel import Channel
from ..controller.base import Endpoint


@dataclass
class Node(object):
    label: str
    endpoints: List[str]
    inputs: List[str]
    outputs: List[str]

    @property
    def node_id(self) -> str:
        return str(id(self))

    def to_dot(self) -> Iterable[str]:
        r = [f"subgraph cluster_{self.node_id} {{"]
        r.append(f'graph [label = "{self.label}" bgcolor = "#bec3c6"]')
        if self.endpoints:
            ep_label = "|".join(f"<{ep}>{ep}" for ep in self.endpoints)
            r.append(f'ep_{self.node_id} [shape = record label = "{ep_label}"]')
        if self.inputs:
            in_label = "|".join(f"<{i}>{i}" for i in self.inputs)
            r.append(f'in_{self.node_id} [shape = record label = "{in_label}"]')
        if self.outputs:
            out_label = "|".join(f"<{o}>{o}" for o in self.outputs)
            r.append(f'out_{self.node_id} [shape = record label = "{out_label}"]')
        r.append("}")
        return r

    def get_ref(self, name: str) -> str:
        if name in self.endpoints:
            return f"ep_{self.node_id}:{name}"
        if name in self.inputs:
            return f"in_{self.node_id}:{name}"
        if name in self.outputs:
            return f"out_{self.node_id}:{name}"
        msg = "Invalid ref"
        raise ValueError(msg)

    def add_input(self, ep: str) -> None:
        if ep not in self.inputs and ep not in self.endpoints:
            self.inputs.append(ep)

    def add_output(self, ep: str) -> None:
        if ep not in self.outputs and ep not in self.endpoints:
            self.outputs.append(ep)

    def add_endpoint(self, ep: str) -> None:
        if ep not in self.endpoints:
            self.endpoints.append(ep)


class BaseMapper(object):
    name: str = "base"

    def __init__(self, channel: Channel):
        self.logger = PrefixLoggerAdapter(logging.getLogger("tracer"), self.name)
        self.channel = channel

    def to_dot(
        self,
        start: Optional[Endpoint] = None,
        end: Optional[Endpoint] = None,
        connect_input: Optional[str] = None,
        connect_output: Optional[str] = None,
    ) -> str:
        raise NotImplementedError
