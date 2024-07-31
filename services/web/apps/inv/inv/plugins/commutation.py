# ---------------------------------------------------------------------
# inv.inv commutation plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Iterable, Tuple, Dict, DefaultDict, Any, Set
from collections import defaultdict

# Third party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from .base import InvPlugin


@dataclass
class ConnectionItem(object):
    local_name: str
    remote_object: str
    remote_name: str


@dataclass
class Node(object):
    object_id: str
    name: str
    model: str
    parent_connection: Optional[str]
    children: List["Node"]
    is_external: bool
    connections: List[ConnectionItem]

    @classmethod
    def from_object(cls, obj: Object) -> "Node":
        return Node(
            object_id=str(obj.id),
            name=obj.name or "",
            model=obj.model.get_short_label(),
            parent_connection=None,
            children=[],
            is_external=False,
            connections=[],
        )

    @property
    def is_chassis(self) -> bool:
        """
        Check if box is chassis.

        Returns:
            True: if node is chassis
        """
        if self.parent_connection:
            return False
        return any(bool(c.parent_connection) for c in self.children)


class CommutationPlugin(InvPlugin):
    name = "commutation"
    js = "NOC.inv.inv.plugins.commutation.CommutationPanel"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, object):
        return {"data": self.to_viz(self.get_nested_inventory(object))}

    @staticmethod
    def iter_indent(s: Iterable[str], i: int = 0) -> Iterable[str]:
        """
        Indent iterable.

        Args:
            s: Input iterable of strings
            i: Indentation level

        Returns:
            Indented strings
        """
        if not i:
            yield from s
        else:
            for item in s:
                yield "  " * i + item

    def get_nested_inventory(self, obj: Object) -> Iterable[Node]:
        """
        Fetch object and all underlying objects.

        Args:
            obj: Object instance

        Returns:
            Iterable of Node
        """

        def get_outer(obj: Object) -> Optional[Tuple[Object, str]]:
            for _, c, n in obj.iter_outer_connections():
                return c, n
            return None

        def add_external(obj: Object) -> Node:
            """
            Append external node and parents.
            """
            node = Node.from_object(obj)
            node.external = True
            nodes[node.object_id] = node
            parent = None
            if not obj.container:
                cc = get_outer(obj)
                if cc:
                    oo, parent_connection = cc
                    # Add parent
                    parent = nodes.get(str(oo.id))
                    if not parent:
                        # Register parent
                        parent = add_external(oo)
                    parent.children.append(node)
                    node.parent_connection = parent_connection
            if parent is None:
                ext_nodes_roots.add(node.object_id)
            return node

        root = str(obj.id)
        # Get objects by hierarchy
        hier_ids = obj.get_nested_ids()
        nodes: Dict[str, Node] = {}
        omap = {}
        containers: List[Tuple[str, str]] = []  # (node_id, container_id)
        for o in Object.objects.filter(id__in=hier_ids):
            omap[o.id] = o
            node = Node.from_object(o)
            nodes[node.object_id] = node
            if o.container:
                containers.append((node.object_id, str(o.container.id)))
        # Link containers
        for node_id, c_id in containers:
            node = nodes[node_id]
            container = nodes.get(c_id)
            if container:
                container.children.append(node)
        # Find vertical and horizontal connections
        wave = list(omap)
        cables = {}
        while wave:
            new_wave = []
            for c in ObjectConnection.objects.filter(connection__object__in=wave):
                if len(c.connection) != 2:
                    continue  # @todo: Process later
                if c.connection[0].object.id in omap:
                    local = c.connection[0]
                    remote = c.connection[1]
                else:
                    local = c.connection[1]
                    remote = c.connection[0]
                if remote.object.id in omap:
                    continue  # Already processed
                if remote.object.model.get_data("length", "length"):
                    cables[remote.object.id] = remote.object
                else:
                    omap[remote.object.id] = remote.object
                    node = Node.from_object(remote.object)
                    node.parent_connection = local.name
                    nodes[node.object_id] = node
                    # Add children
                    nodes[str(local.object.id)].children.append(node)
                    new_wave.append(remote.object.id)
            wave = new_wave
        # Process cables found
        conns: DefaultDict[ObjectId] = defaultdict(list)
        ext_nodes_roots = set()
        for c in ObjectConnection.objects.filter(connection__object__in=list(cables)):
            if len(c.connection) != 2:
                continue  # @todo: Process later
            if c.connection[0].object.id in cables:
                co = c.connection[1]
                conns[c.connection[0].object.id].append((co.object.id, co.name))
            elif c.connection[1].object.id in cables:
                co = c.connection[0]
                conns[c.connection[1].object.id].append((co.object.id, co.name))
            if co.object.id not in omap:
                # External object
                add_external(co.object)
        for items in conns.values():
            if len(items) != 2:
                continue
            nodes[str(items[0][0])].connections.append(
                ConnectionItem(
                    local_name=items[0][1], remote_object=str(items[1][0]), remote_name=items[1][1]
                )
            )
            nodes[str(items[1][0])].connections.append(
                ConnectionItem(
                    local_name=items[1][1], remote_object=str(items[0][0]), remote_name=items[0][1]
                )
            )
        # Root node
        yield self.prune_node(nodes[root])
        # External nodes
        for ext in ext_nodes_roots:
            yield self.prune_node(nodes[ext])

    def prune_node(self, node: Node) -> Node:
        """
        Prune all unconnected nodes.

        Leave only nodes which having connection
        or having any descendant with connections.

        Args:
            node: Node instance

        Returns:
            Pruned node
        """

        def pruned_child(n: Node) -> Optional[None]:
            if not n.children and not n.connections:
                return None
            if not n.children and n.connections:
                return n
            new_children = []
            for c in n.children:
                pc = pruned_child(c)
                if pc:
                    new_children.append(pc)
            if not new_children and not n.connections:
                return None
            n.children = new_children
            return n

        return pruned_child(node)

    def to_viz(self, nodes: Iterable[Node]) -> Dict[str, Any]:
        """
        Render nodes to viz-js JSON

        Args:
            nodes: Iterable of Node

        Returns:
            JSON document describing charts
        """

        def get_label(name: str, model: str) -> str:
            parts = []
            if name:
                parts.append(name)
            if model:
                parts.append(model)
            return "\\n".join(parts)

        def get_graph_template() -> Dict[str, Any]:
            """Get graph template."""
            return {"graphAttributes": {}, "nodes": [], "edges": [], "subgraphs": []}

        def render(node: Node, r: Dict[str, Any]) -> None:
            """Render node to given parent."""
            if node.children:
                render_subgraph(node, r)
            else:
                render_node(node, r)
            # Render connections
            if node.connections:
                for c in node.connections:
                    add_connection(
                        local_object=node.object_id,
                        local_name=c.local_name,
                        remote_object=c.remote_object,
                        remote_name=c.remote_name,
                    )

        def render_subgraph(node: Node, r: Dict[str, Any]) -> None:
            g = get_graph_template()
            g["graphAttributes"]["label"] = get_label(node.name, node.model)
            g["name"] = f"cluster_{node.object_id}"
            # Attach as subgraph
            r["subgraphs"].append(g)
            # Set style
            if node.is_chassis:
                g["graphAttributes"]["style"] = "box"
                g["graphAttributes"]["bgcolor"] = "#bec3c6"
                g["graphAttributes"]["color"] = "black"
            else:
                g["graphAttributes"]["style"] = "rounded,dashed"
                g["graphAttributes"]["color"] = "#919191"
            # Render nested children
            for child in node.children:
                render(child, g)
            # Render slots
            if node.connections:
                g["nodes"].append(
                    {
                        "name": q_node(node.object_id),
                        "attributes": {
                            "shape": "record",
                            "label": "|".join(get_conn(s.local_name) for s in node.connections),
                        },
                    }
                )

        def render_node(node: Node, r: Dict[str, Any]) -> None:
            slots = [
                get_label(
                    node.parent_connection if node.parent_connection else node.name, node.model
                )
            ]
            slots.extend(get_conn(s.local_name) for s in node.connections)
            # Append node
            r["nodes"].append(
                {
                    "name": q_node(node.object_id),
                    "attributes": {"shape": "record", "label": "|".join(slots)},
                }
            )

        def q_node(s: str) -> str:
            """
            Generate node name from id
            """
            return f"obj_{s}"

        def q_conn_name(s: str) -> str:
            """
            Quote connection name
            """
            # @todo: Implement properly
            return s

        def q_conn_label(s: str) -> str:
            """
            Quote connection label
            """
            # @todo: Implement properly
            return s

        def get_conn(name: str) -> str:
            """
            Generate record item representing connections.
            """
            return f"<{q_conn_name(name)}>{q_conn_label(name)}"

        def add_connection(
            local_object: str, local_name: str, remote_object: str, remote_name: str
        ) -> None:
            # Calculate stable hash
            if local_object == remote_object:
                # Loop
                if local_name < remote_name:
                    c_hash = f"{local_object}|{local_name}|{remote_object}|{remote_name}"
                else:
                    c_hash = f"{local_object}|{remote_name}|{remote_object}|{local_name}"
            elif local_object < remote_object:
                c_hash = f"{local_object}|{local_name}|{remote_object}|{remote_name}"
            else:
                c_hash = f"{remote_object}|{remote_name}|{local_object}|{local_name}"
            # Check if we have seen this connection
            if c_hash in seen_conns:
                return
            # Generate connnection edge
            edge = {
                "tail": q_node(local_object),
                "head": q_node(remote_object),
                "attributes": {
                    "tailport": q_conn_name(local_name),
                    "headport": q_conn_name(remote_name),
                },
            }
            top["edges"].append(edge)
            # Add to seen connections
            seen_conns.add(c_hash)

        seen_conns: Set[str] = set()
        top = get_graph_template()
        top["directed"] = False
        top["graphAttributes"]["rankdir"] = "LR"
        top["graphAttributes"]["bgcolor"] = ""  # Prevent attribute propagation
        top["graphAttributes"]["label"] = ""  # And here too
        top["edgeAttributes"] = {"penwidth": 2}
        for node in nodes:
            if not node:
                continue  # Pruned
            render(node, top)
        return top
