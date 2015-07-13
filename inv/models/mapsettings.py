## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map Settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField,
                                ListField, FloatField,
                                EmbeddedDocumentField)

logger = logging.getLogger(__name__)

LC_NORMAL = "normal"
LC_SMOOTH = "smooth"
LC_ROUNDED = "rounded"


class NodeSettings(EmbeddedDocument):
    type = StringField()
    id = StringField()
    x = FloatField()
    y = FloatField()

    def __unicode__(self):
        return "%s:%s" % (self.type, self.id)


class VertexPosition(EmbeddedDocument):
    x = FloatField()
    y = FloatField()

    def __unicode__(self):
        return u"(%s, %s)" % (self.x, self.y)


class LinkSettings(EmbeddedDocument):
    type = StringField()
    id = StringField()
    connector = StringField(
        choices=[
            (LC_NORMAL, "Normal"),
            (LC_SMOOTH, "Smooth"),
            (LC_ROUNDED, "Rounded")
        ], default=LC_NORMAL
    )
    vertices = ListField(EmbeddedDocumentField(VertexPosition))

    def __unicode__(self):
        return "%s:%s" % (self.type, self.id)


class MapSettings(Document):
    meta = {
        "collection": "noc.mapsettings"
    }

    # Segment or selector id
    segment = StringField(unique=True)
    # Change time
    changed = DateTimeField()
    # Changing user
    user = StringField()
    # Paper size
    width = FloatField()
    height = FloatField()
    #
    nodes = ListField(EmbeddedDocumentField(NodeSettings))
    links = ListField(EmbeddedDocumentField(LinkSettings))

    def __unicode__(self):
        return self.segment

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
            d = MapSettings(
                segment=data["id"],
                nodes=[],
                links=[]
            )
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
            nn += [NodeSettings(
                type=nd["type"],
                id=nd["id"],
                x=nd["x"],
                y=nd["y"]
            )]
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
            nl = new_links.get((n.type, n.id))
            if not nl:
                continue  # Not found
            l.vertices = nl["vertices"]
            l.connector = nl.get("connector", LC_NORMAL)
            nn += [nl]
            del new_links[(l.type, l.id)]
        for l in new_links:
            nl = new_links[l]
            nn += [LinkSettings(
                type=nl["type"],
                id=nl["id"],
                vertices=nl.get("vertices", []),
                connector=nl.get("connector", "normal")
            )]
        d.links = [l for l in sorted(nn, key=lambda x: (x.type, x.id))
                   if l.vertices or l.connector != LC_NORMAL]
        # Finally save
        d.save()
        return d
