# ---------------------------------------------------------------------
# Map Settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Optional
import datetime
import logging

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ListField,
    FloatField,
    EmbeddedDocumentField,
    IntField,
    DictField,
    BooleanField,
)

# NOC modules
from noc.core.topology.loader import loader as t_loader
from noc.core.topology.base import TopologyBase

logger = logging.getLogger(__name__)

LC_NORMAL = "normal"
LC_SMOOTH = "smooth"
LC_ROUNDED = "rounded"


class NodeSettings(EmbeddedDocument):
    type = StringField()
    id = StringField()
    x = FloatField()
    y = FloatField()

    def __str__(self):
        return "%s:%s" % (self.type, self.id)


class VertexPosition(EmbeddedDocument):
    x = FloatField()
    y = FloatField()

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)


class LinkSettings(EmbeddedDocument):
    type = StringField()
    id = StringField()
    connector = StringField(
        choices=[(LC_NORMAL, "Normal"), (LC_SMOOTH, "Smooth"), (LC_ROUNDED, "Rounded")],
        default=LC_NORMAL,
    )
    vertices = ListField(EmbeddedDocumentField(VertexPosition))

    def __str__(self):
        return "%s:%s" % (self.type, self.id)


class MapSettings(Document):
    meta = {
        "collection": "noc.mapsettings",
        "strict": False,
        "auto_create_index": False,
        "indexes": [{"fields": ["gen_type", "gen_id"], "unique": True}],
    }

    # Generator type
    gen_type = StringField()
    # Generator ID param
    gen_id = StringField()
    # Generator version
    gen_version = IntField(min_value=0)
    # Change time
    last_change_id = DateTimeField()
    current_change_id = DateTimeField(default=datetime.datetime.now())
    # Changing user
    user = StringField()
    # Paper size
    width = FloatField()
    height = FloatField()
    # Paper image
    # Gen data
    # get_data =
    # Generator Hints
    force_layout = BooleanField()  # Always rebuild layout hints
    gen_hints = DictField()
    #
    nodes = ListField(EmbeddedDocumentField(NodeSettings))
    links = ListField(EmbeddedDocumentField(LinkSettings))

    def __str__(self):
        return f"{self.gen_type}: {self.gen_id} ({self.gen_version})"

    def get_nodes(self):
        """
        Returns a dict of id -> Node settings
        """
        nodes = {}
        for n in self.nodes:
            nodes[n.node] = n
        return nodes

    @classmethod
    def load_json(cls, data, user=None):
        """
        Load json data of:
        id
        nodes:
            id
            x
            y
        links:
            id
            vertices:
                x
                y
        """
        d = MapSettings.objects.filter(gen_type=data["gen_type"], gen_id=data["id"]).first()
        if d:
            logger.info("[%s|%s] Updating settings for map", data["gen_type"], data["id"])
        else:
            logger.info("[%s|%s] Creating new settings", data["gen_type"], data["id"])
            d = MapSettings(gen_type=data["gen_type"], gen_id=data["id"], nodes=[], links=[])
        d.update_settings(data.get("nodes", []), data.get("links", []), user=user)
        return d

    def update_settings(self, nodes, links, user: Optional[str] = None):
        """
        Update settings
        :param nodes:
        :param links:
        :param user:
        :return:
        """
        self.current_change_id = datetime.datetime.now().replace(microsecond=0)
        if user:
            self.user = user
        # Update nodes
        new_nodes = {}  # id -> data
        for n in nodes:
            new_nodes[(n["type"], n["id"])] = n
        nn = []
        for n in self.nodes:
            nd = new_nodes.get((n.type, n.id))
            if not nd:
                continue  # Not found
            n.x = nd["x"]
            n.y = nd["y"]
            nn += [n]
            del new_nodes[(n.type, n.id)]
        mx = 0.0
        my = 0.0
        for n in new_nodes:
            nd = new_nodes[n]
            nn += [NodeSettings(type=nd["type"], id=nd["id"], x=nd["x"], y=nd["y"])]
            mx = max(mx, nd["x"])
            my = max(my, nd["y"])
        # self.width = data.get("width", mx)
        # self.height = data.get("height", my)
        self.nodes = sorted(nn, key=lambda x: (x.type, x.id))
        # Update links
        new_links = {}
        for ll in links:
            new_links[(ll["type"], ll["id"])] = ll
        nn = []
        for ll in self.links:
            nl = new_links.get((ll.type, ll.id))
            if not nl:
                continue  # Not found
            ll.vertices = [VertexPosition(x=v["x"], y=v["y"]) for v in nl.get("vertices", [])]
            ll.connector = nl.get("connector", LC_NORMAL)
            nn += [ll]
            del new_links[(ll.type, ll.id)]
        for ll in new_links:
            nl = new_links[ll]
            nn += [
                LinkSettings(
                    type=nl["type"],
                    id=nl["id"],
                    vertices=[VertexPosition(x=v["x"], y=v["y"]) for v in nl.get("vertices", [])],
                    connector=nl.get("connector", "normal"),
                )
            ]
        self.links = [
            ll
            for ll in sorted(nn, key=lambda x: (x.type, x.id))
            if ll.vertices or ll.connector != LC_NORMAL
        ]
        # Finally save
        self.save()

    @classmethod
    def get_map(cls, gen_id: str, gen_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Return Map Data
        :param gen_id: Generator Id param
        :param gen_type: Generator Type
        :param kwargs: generator Hints
        :return:
        """
        gen = t_loader[gen_type]
        if not gen:
            logger.warning("Unknown generator: %s", gen_type)
            raise ValueError("Unknown Map Type: %s", gen_type)
        settings: MapSettings = MapSettings.objects.filter(gen_type=gen_type, gen_id=gen_id).first()
        node_hints = {}
        link_hints = {}
        if settings:
            logger.info("[%s|%s] Using stored positions", gen_type, gen_id)
            for n in settings.nodes:
                node_hints[n.id] = {"type": n.type, "id": n.id, "x": n.x, "y": n.y}
            for ll in settings.links:
                link_hints[ll.id] = {
                    "connector": ll.connector if len(ll.vertices) else "normal",
                    "vertices": [{"x": v.x, "y": v.y} for v in ll.vertices],
                }
            layout = settings.force_layout
        else:
            logger.info("[%s|%s] Create new settings", gen_type, gen_id)
            settings = MapSettings(gen_type=gen_type, gen_id=gen_id, nodes=[], links=[])
            layout = True
        # Generate topology
        topology: TopologyBase = gen(gen_id, node_hints, link_hints, **kwargs)
        if layout:
            logger.info("[%s|%s] Generating positions", gen_type, gen_id)
            topology.layout()
            settings.update_settings(
                nodes=[
                    {"type": n["type"], "id": n["id"], "x": n["x"], "y": n["y"]}
                    for n in topology.G.nodes.values()
                    if n.get("x") is not None and n.get("y") is not None
                ],
                links=[
                    {
                        "type": n["type"],
                        "id": n["id"],
                        "vertices": n.get("vertices", []),
                        "connector": n.get("connector", "normal"),
                    }
                    for n in topology.G.edges.values()
                ],
            )
        return {
            "id": str(gen_id),
            "type": gen_type,
            "max_links": 1000,
            "name": topology.title,
            "caps": list(topology.caps),
            "nodes": [x for x in topology.iter_nodes()],
            "links": [ll for ll in topology.iter_edges()],
        }
