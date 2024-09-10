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
from noc.core.hash import hash_int
from .base import InvPlugin


@dataclass
class ConnectionItem(object):
    local_name: str
    remote_object: str
    remote_name: str


@dataclass
class Node(object):
    object: Object
    name: str
    model: str
    parent_connection: Optional[str]
    children: List["Node"]
    is_external: bool
    connections: List[ConnectionItem]

    @classmethod
    def from_object(cls, obj: Object) -> "Node":
        return Node(
            object=obj,
            name=obj.name or "",
            model=obj.model.get_short_label(),
            parent_connection=obj.parent_connection,
            children=[],
            is_external=False,
            connections=[],
        )

    @property
    def object_id(self) -> str:
        return str(self.object.id)

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

    def get_data(self, request, obj):
        inv = list(self.iter_nested_inventory(obj))
        return {"viz": self.to_viz(inv), "data": self.to_data(inv)}

    @staticmethod
    def c_hash(local_object: str, local_name: str, remote_object: str, remote_name: str) -> str:
        """
        Get stable connection hash.
        """

        def inner() -> str:
            # Calculate stable hash
            if local_object == remote_object:
                # Loop
                if local_name < remote_name:
                    return f"{local_object}|{local_name}|{remote_object}|{remote_name}"
                return f"{local_object}|{remote_name}|{remote_object}|{local_name}"
            elif local_object < remote_object:
                return f"{local_object}|{local_name}|{remote_object}|{remote_name}"
            return f"{remote_object}|{remote_name}|{local_object}|{local_name}"

        return f"e_{hash_int(inner())}"

    def iter_nested_inventory(self, obj: Object) -> Iterable[Node]:
        """
        Fetch object and all underlying objects.

        Args:
            obj: Object instance

        Returns:
            Iterable of Node
        """

        def add_external(obj: Object) -> Node:
            """
            Append external node and parents.
            """
            node = Node.from_object(obj)
            node.external = True
            nodes[node.object_id] = node
            parent = None
            if obj.parent_connection:
                # Add parent
                parent = nodes.get(str(obj.parent.id))
                if not parent:
                    # Register parent
                    parent = add_external(obj.parent)
                parent.children.append(node)
                node.parent_connection = obj.parent_connection
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
            if o.parent:
                containers.append((node.object_id, str(o.parent.id)))
        # Link containers
        for node_id, c_id in containers:
            node = nodes[node_id]
            container = nodes.get(c_id)
            if container:
                container.children.append(node)
        # Get cable objects
        cables = {}
        for c in ObjectConnection.objects.filter(connection__object__in=list(omap)):
            if len(c.connection) != 2:
                continue  # @todo: Process later
            if c.connection[0].object.id in omap:
                remote = c.connection[1]
            else:
                remote = c.connection[0]
            if remote.object.id in omap:
                continue  # Already processed
            if remote.object.model.get_data("length", "length"):
                cables[remote.object.id] = remote.object
        # Get other side of cables
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
        # Create connections for cables
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
        node = self.prune_node(nodes[root])
        if node:
            yield node
        # External nodes
        for ext in ext_nodes_roots:
            node = self.prune_node(nodes[ext])
            if node:
                yield node

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

        def pruned_child(n: Node) -> Optional[Node]:
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
            g["graphAttributes"]["label"] = get_label(
                node.parent_connection if node.parent_connection else node.name, node.model
            )
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
            # Check if we have seen this connection
            c_hash = self.c_hash(local_object, local_name, remote_object, remote_name)
            if c_hash in seen_conns:
                return
            # Generate connnection edge
            edge = {
                "tail": q_node(local_object),
                "head": q_node(remote_object),
                "attributes": {
                    "id": c_hash,
                    "tailport": q_conn_name(local_name),
                    "headport": q_conn_name(remote_name),
                    "class": "selectable",
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

    def to_data(self, nodes: Iterable[Node]) -> List[Dict[str, Any]]:
        """
        Prepare commutation table
        """

        def update_labels(node: None) -> None:
            if node.object_id in node_labels:
                return
            # Build label
            parts = []
            local_name = node.object.get_local_name_path(True)
            if local_name:
                parts.append(" > ".join(local_name))
            else:
                parts.append(node.name)
            parts.append(f" [{node.object.model.get_short_label()}]")
            label = "".join(parts)
            node_labels[node.object_id] = label
            # Update children
            for child in node.children:
                update_labels(child)

        def collect(node: Node) -> None:
            for c in node.connections:
                c_hash = self.c_hash(
                    local_object=node.object_id,
                    local_name=c.local_name,
                    remote_object=c.remote_object,
                    remote_name=c.remote_name,
                )
                if c_hash in seen:
                    continue
                data.append(
                    {
                        "id": c_hash,
                        "local_object": node.object_id,
                        "local_object__label": node_labels[node.object_id],
                        "local_name": c.local_name,
                        "remote_object": c.remote_object,
                        "remote_object__label": node_labels[c.remote_object],
                        "remote_name": c.remote_name,
                    }
                )
                seen.add(c_hash)
            for child in node.children:
                collect(child)

        # Collect node labels
        node_labels: Dict[str, str] = {}
        for node in nodes:
            update_labels(node)
        #
        data = []
        seen = set()
        # Collect connections
        for node in nodes:
            collect(node)
        return data
