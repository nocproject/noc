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
    meta = {"collection": "noc.mapsettings", "strict": False, "auto_create_index": False}

    # Generator type
    gen_type = StringField()
    # Generator ID param
    gen_id = StringField()
    # Generator version
    gen_version = IntField(min_value=0)
    # Change time
    last_change_id = DateTimeField()
    current_change_id = DateTimeField()
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
        return f"{self.get_type}: {self.gen_id} ({self.gen_version})"

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
        d = MapSettings.objects.filter(segment=data["id"]).first()
        if d:
            logger.info("Updating settings for %s", data["id"])
        else:
            logger.info("Creating new settings for %s", data["id"])
            d = MapSettings(segment=data["id"], nodes=[], links=[])
        # Update meta
        if user:
            d.user = user
        d.changed = datetime.datetime.now()
        # Update nodes
        new_nodes = {}  # id -> data
        for n in data.get("nodes", []):
            new_nodes[(n["type"], n["id"])] = n
        nn = []
        for n in d.nodes:
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
        d.width = data.get("width", mx)
        d.height = data.get("height", my)
        d.nodes = sorted(nn, key=lambda x: (x.type, x.id))
        # Update links
        new_links = {}
        for l in data.get("links", []):
            new_links[(l["type"], l["id"])] = l
        nn = []
        for l in d.links:
            nl = new_links.get((l.type, l.id))
            if not nl:
                continue  # Not found
            l.vertices = [VertexPosition(x=v["x"], y=v["y"]) for v in nl.get("vertices", [])]
            l.connector = nl.get("connector", LC_NORMAL)
            nn += [l]
            del new_links[(l.type, l.id)]
        for l in new_links:
            nl = new_links[l]
            nn += [
                LinkSettings(
                    type=nl["type"],
                    id=nl["id"],
                    vertices=[VertexPosition(x=v["x"], y=v["y"]) for v in nl.get("vertices", [])],
                    connector=nl.get("connector", "normal"),
                )
            ]
        d.links = [
            l
            for l in sorted(nn, key=lambda x: (x.type, x.id))
            if l.vertices or l.connector != LC_NORMAL
        ]
        # Finally save
        d.save()
        return d

    def update_settings(self, nodes, links):
        """
        Update settings
        :param nodes:
        :param links:
        :return:
        """
        ...

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
            return
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
        else:
            logger.info("[%s|%s] Generating positions", gen_type, gen_id)
        # Generate topology
        topology: TopologyBase = gen(gen_id, node_hints, link_hints, **kwargs)
        if not settings or settings.force_layout:
            topology.layout()
            # settings.update_settings(
            #     nodes=[
            #         {"type": n["type"], "id": n["id"], "x": n["x"], "y": n["y"]}
            #         for n in r["nodes"]
            #         if n.get("x") is not None and n.get("y") is not None
            #     ],
            #     links=[
            #         {
            #             "type": n["type"],
            #             "id": n["id"],
            #             "vertices": n.get("vertices", []),
            #             "connector": n.get("connector", "normal"),
            #         }
            #         for n in r["links"]
            #     ],
            # )
        return {
            "id": str(gen_id),
            "type": gen_type,
            "max_links": 1000,
            "name": topology.title,
            "caps": list(topology.caps),
            "nodes": [x for x in topology.iter_nodes()],
            "links": [ll for ll in topology.iter_edges()],
        }
