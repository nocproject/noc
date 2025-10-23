# ---------------------------------------------------------------------
# Map Settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
)
from mongoengine.queryset.visitor import Q
from mongoengine.errors import NotUniqueError

# NOC modules
from noc.core.topology.loader import loader as t_loader
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import Layout
from noc.config import config

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
    # Generator Params
    gen_params = DictField()
    # Change time
    last_change_id = DateTimeField()
    current_change_id = DateTimeField(default=datetime.datetime.now())
    # Changing user
    user = StringField()
    # Paper size
    width = FloatField()
    height = FloatField()
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

    def get_generator_hints(self, **kwargs) -> Dict[str, str]:
        """
        Return Hints settings for generator
        :param kwargs: Additional hints
        :return:
        """
        node_hints, link_hints = {}, {}
        r = kwargs or {}
        if self.gen_params:
            r.update(self.gen_params)
        for n in self.nodes:
            node_hints[n.id] = {"type": n.type, "id": n.id, "x": n.x, "y": n.y}
        for ll in self.links:
            link_hints[ll.id] = {
                "connector": ll.connector if len(ll.vertices) else "normal",
                "vertices": [{"x": v.x, "y": v.y} for v in ll.vertices],
            }
        r["node_hints"] = node_hints
        r["link_hints"] = link_hints
        return r

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
        d = cls.ensure_settings(gen_type=data["gen_type"], gen_id=data["id"])
        d.update_settings(
            data.get("nodes", []),
            data.get("links", []),
            user=user,
            width=data.get("width"),
            height=data.get("height"),
        )
        return d

    def update_settings(
        self,
        nodes,
        links,
        user: Optional[str] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ):
        """
        Update settings
        :param nodes:
        :param links:
        :param user:
        :param width:
        :param height:
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
        self.width = float(width or mx)  # If not convert float - Validation error as None
        self.height = float(height or my)  # If convert float - Validation error as None
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
        try:
            self.save()
        except NotUniqueError:
            # Already saved settings
            pass

    @classmethod
    def ensure_settings(cls, gen_type: str, gen_id, **kwargs) -> "MapSettings":
        """
        Ensure MapSettings Exists and create it if not
        :param gen_type:
        :param gen_id:
        :param kwargs:
        :return:
        """
        gen_id = str(gen_id)
        q = Q(gen_type=gen_type, gen_id=gen_id)
        if kwargs:
            q |= Q(gen_type=gen_type, gen_params=kwargs)
        settings = MapSettings.objects.filter(q).first()
        if settings:
            logger.info("[%s|%s|%s] Using stored positions", gen_type, gen_id, kwargs)
            return settings
        logger.info("[%s|%s|%s] Create new settings", gen_type, gen_id, kwargs)
        settings = MapSettings(gen_type=gen_type, gen_id=gen_id, nodes=[], links=[])
        if kwargs:
            settings.gen_params = kwargs.copy()
        return settings

    def is_change_layout(self, topology: TopologyBase) -> bool:
        """
        Check rebuild layout needed
        :param topology:
        :return:
        """
        if topology.meta.layout == Layout("FA"):
            # Always rebuild layout
            return True
        if len(self.nodes) != len(topology.G.nodes):
            # Change node count
            return True
        if (topology.meta.width and self.width != topology.meta.width) or (
            topology.meta.height and self.height != topology.meta.height
        ):
            # Change Map Size
            return True
        return False

    @classmethod
    def get_map(
        cls, gen_type: str, gen_id: Optional[str] = None, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Return Map Data
        :param gen_id: Generator Id param
        :param gen_type: Generator Type
        :param kwargs: generator Hints
        :return:
        """
        gen: TopologyBase = t_loader[gen_type]
        if not gen:
            logger.warning("Unknown generator: %s", gen_type)
            raise ValueError(f"Unknown Map Type: {gen_type}")
        params = {k: v for k, v in kwargs.items() if k in gen.PARAMS}
        if gen.PARAMS and not params and not gen_id:
            raise ValueError(f"Generator {gen_type} required params: {gen.PARAMS}")
        # Getting Map settings
        settings = cls.ensure_settings(gen_type, gen_id, **params)
        # Getting hints
        hints = settings.get_generator_hints()
        # Generate topology
        logger.debug("[%s] Build topology by param: %s", gen_type, hints)
        topology: TopologyBase = gen(gen_id, **hints)
        if settings.is_change_layout(topology):
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
                height=topology.meta.height,
                width=topology.meta.width,
            )
        background = topology.meta.image
        return {
            "id": str(gen_id),
            "type": gen_type,
            # Map Params
            "max_links": topology.meta.max_links,
            "grid_size": config.web.topology_map_grid_size,
            "normalize_position": topology.NORMALIZE_POSITION,
            "object_status_refresh_interval": topology.meta.object_status_refresh_interval,
            "background_image": background.image if background else None,
            "background_opacity": background.opacity if background else None,
            # Hint params
            "name": topology.title,
            "width": settings.width or 0.0,
            "height": settings.height or 0.0,
            "caps": list(topology.caps),
            "nodes": list(topology.iter_nodes()),
            "links": list(topology.iter_edges()),
        }
