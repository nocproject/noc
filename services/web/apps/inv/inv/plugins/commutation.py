# ---------------------------------------------------------------------
# inv.inv commutation plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Iterable, Tuple, Dict, DefaultDict
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
        return {"dot": self.to_dot(self.get_nested_inventory(object))}

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
        for o in Object.objects.filter(id__in=hier_ids):
            omap[o.id] = o
            node = Node.from_object(o)
            nodes[node.object_id] = node
            if o.container:
                c_id = str(o.container.id)
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

    def to_dot(self, nodes: Iterable[Node]) -> str:
        """
        Render nodes to .dot

        Args:
            nodes: Iterable of Node

        Returns:
            Formatted graphviz document
        """

        def q(s: str) -> str:
            return s.replace('"', '\\"')

        def q_id(s: str) -> str:
            return s.replace(" ", "_")

        def dot_label(name: str, model: str) -> str:
            parts = []
            if name:
                parts.append(name)
            if model:
                parts.append(model)
            return q("\\n".join(parts))

        def c_hash(node: None, c: ConnectionItem) -> str:
            if node.object_id < c.remote_object:
                return f"{node.object_id}|{c.local_name}|{c.remote_object}|{c.remote_name}"
            return f"{c.remote_object}|{c.remote_name}|{node.object_id}|{c.local_name}"

        def render(node: Node, level: int = 0) -> Tuple[List[str], List[str]]:
            r = []
            c = []
            if node.children:
                if node.is_chassis:
                    style = 'style = box bgcolor = "#bec3c6" color = black'
                else:
                    style = 'style = "rounded,dashed" color = "#919191"'
                r += [
                    f"subgraph cluster_{node.object_id} {{",
                    f'  graph [label = "{dot_label(node.name, node.model)}" {style}]',
                ]
                for child in node.children:
                    cr, cc = render(child, 1)
                    r.extend(cr)
                    c.extend(cc)
                if node.connections:
                    slots = [f"<{s.local_name}>{s.local_name}" for s in node.connections]
                    r.append(
                        f"  obj_{node.object_id} [shape = record label = \"{'|'.join(slots)}\"]"
                    )
                r.append("}")
            else:
                slots = [
                    dot_label(
                        node.parent_connection if node.parent_connection else node.name, node.model
                    )
                ] + [f"<{s.local_name}>{s.local_name}" for s in node.connections]
                r.append(f"obj_{node.object_id} [shape=record label=\"{'|'.join(slots)}\"]")
            if node.connections:
                for s in node.connections:
                    h = c_hash(node, s)
                    if h in seen_conns:
                        continue
                    c.append(
                        f"obj_{node.object_id}:{q_id(s.local_name)} -- obj_{s.remote_object}:{q_id(s.remote_name)}"
                    )
                    seen_conns.add(h)
            return list(self.iter_indent(r, level)), c

        r = ["graph {", "  graph [rankdir = LR]"]
        conns = []
        seen_conns = set()
        for node in nodes:
            if not node:
                continue  # Pruned
            g, c = render(node, 1)
            r.extend(g)
            conns.extend(c)
        # Inject connections
        r.extend(self.iter_indent(conns, 1))
        r.append("}")
        return "\n".join(r)
