# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generate Mapnik XML for Map object
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from xml.dom.minidom import Document
## NOC modules
from noc.gis.models import Style, FontSet
from noc.settings import config


SYMBOLIZERS = dict((s.lower()[:-10], s) for s in (
    "PointSymbolizer", "LinePatternSymbolizer", "PolygonPatternSymbolizer",
    "TextSymbolizer", "ShieldSymbolizer", "LineSymbolizer",
    "PolygonSymbolizer", "BuildingSymbolizer", "RasterSymbolizer",
    "MarkersSymbolizer"))

SYM_PMAP = {
    "min-distance": "minimum-distance"
}


def map_to_xml(m, pretty_xml=False):
    """
    Serialize Map object as Mapnik XML

    :param m: Map instance
    :type m: Map
    :param pretty_xml: Render pretty indented XML if True
    :type pretty_xml: bool
    :return: XML
    :rtype: str
    """
    # <Map>
    doc = Document()
    root = doc.createElement("Map")
    doc.appendChild(root)
    root.setAttribute("background-color", "#b5d0d0")
    root.setAttribute("srs", m.srs.proj4text)
    root.setAttribute("minimum-version", "2.0.0")
    # Get styles and fontsets used
    layers = m.active_layers
    styles = []
    fontsets = []
    for l in layers:
        for sn in l.styles:
            s = Style.objects.filter(name=sn).first()
            if s and s not in styles:
                styles += [s]
                for r in s.rules:
                    for sm in r.symbolizers:
                        if "fontset-name" in sm:
                            fsn = sm["fontset-name"]
                            fs = FontSet.objects.filter(name=fsn).first()
                            if fs and fs not in fontsets:
                                fontsets += [fs]
    # <FontSet>
    for fs in fontsets:
        fontset = doc.createElement("FontSet")
        fontset.setAttribute("name", fs.name)
        for f in fs.fonts:
            font = doc.createElement("Font")
            font.setAttribute("face-name", f)
            fontset.appendChild(font)
        root.appendChild(fontset)
    # <Style>
    for s in styles:
        style = doc.createElement("Style")
        style.setAttribute("name", s.name)
        for r in s.rules:
            # <Rule>
            rule = doc.createElement("Rule")
            if r.minscale_zoom is not None:
                # <MinScaleDenominator>
                t = doc.createElement("MinScaleDenominator")
                t.appendChild(doc.createTextNode(str(r.minscale_zoom)))
                rule.appendChild(t)
            if r.maxscale_zoom is not None:
                # <MaxScaleDenominator>
                t = doc.createElement("MaxScaleDenominator")
                t.appendChild(doc.createTextNode(str(r.maxscale_zoom)))
                rule.appendChild(t)
            if r.rule_filter:
                # <Filter>
                t = doc.createElement("Filter")
                t.appendChild(doc.createTextNode(r.rule_filter))
                rule.appendChild(t)
            # <*Symbolizer>
            for sm in r.symbolizers:
                t = doc.createElement(SYMBOLIZERS[sm["type"]])
                for k in sm:
                    if k == "name":
                        ek = sm[k]
                        if "[" not in ek:
                            ek = "[%s]" % ek
                        t.appendChild(doc.createTextNode(ek))
                    elif k == "cdata":
                        t.appendChild(doc.createTextNode(sm[k]))
                    elif k != "type":
                        ek = k.replace("_", "-")
                        t.setAttribute(SYM_PMAP.get(ek, ek), sm[k])
                rule.appendChild(t)
            style.appendChild(rule)
        root.appendChild(style)
    # <Layer>
    for l in layers:
        layer = doc.createElement("Layer")
        layer.setAttribute("name", l.name)
        layer.setAttribute("status", "on")
        layer.setAttribute("srs", l.srs.proj4text)
        for s in l.styles:
            # <StyleName>
            t = doc.createElement("StyleName")
            t.appendChild(doc.createTextNode(s))
            layer.appendChild(t)
        # <Datasource>
        t = doc.createElement("Datasource")
        ds = l.datasource.copy()
        if ds["type"] == "postgis" and ds["dbname"] == "":
            # Use NOC's database credentials
            ds["dbname"] = config.get("database", "name")
            ds["host"] = config.get("database", "host")
            ds["port"] = config.get("database", "port")
            ds["user"] = config.get("database", "user")
            ds["password"] = config.get("database", "password")
        for k in ds:
            # <Parameter>
            tt = doc.createElement("Parameter")
            tt.setAttribute("name", k)
            tt.appendChild(doc.createTextNode(ds[k]))
            t.appendChild(tt)
        layer.appendChild(t)
        #
        root.appendChild(layer)
    #
    if pretty_xml:
        return doc.toprettyxml()
    else:
        return doc.toxml()
