# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parse OSM XML and return address to coodinates bindings
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from xml.parsers.expat import ParserCreate
## NOC modules
from base import GeocodingParser


class OSMXMLParser(GeocodingParser):
    ID_ADDR = "OSM_ID"

    def __init__(self):
        super(OSMXMLParser, self).__init__()
        self.xml_parser = ParserCreate()
        self.xml_parser.StartElementHandler = self.xml_start_element
        self.xml_parser.EndElementHandler = self.xml_stop_element
        self.current = None
        self.nodes = {}  # id -> (lon, lat, tags)
        self.buildings = []  # {points: ...}

    def xml_start_element(self, name, attrs):
        if name in ("node", "way"):
            self.current = {
                "name": name,
                "attrs": attrs,
                "tags": {},
                "nodes": []
            }
        elif name == "tag":
            self.current["tags"][attrs["k"]] = attrs["v"]
        elif name == "nd":
            self.current["nodes"] += [attrs["ref"]]

    def xml_stop_element(self, name):
        if name == "node":
            a = self.current["attrs"]
            self.nodes[a["id"]] = (a["lon"], a["lat"], self.current["tags"])
        elif name == "way":
            t = self.current["tags"]
            if t.get("building"):
                # Get address
                fp = [
                    t.get("addr:country"),
                    t.get("addr:city"),
                    t.get("addr:street"),
                    t.get("addr:housenumber")
                ]
                addr = ", ".join(x for x in fp if x)
                # Get points
                points = [
                    (float(self.nodes[n][0]), float(self.nodes[n][1]))
                    for n in self.current["nodes"]
                ]
                self.feed_building(self.current["attrs"]["id"],
                                   addr, self.get_centroid(points))

    def parse(self, f):
        self.xml_parser.ParseFile(f)
