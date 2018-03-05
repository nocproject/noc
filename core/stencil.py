# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Stencil Registry
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import logging
from collections import namedtuple
from operator import itemgetter
from xml.etree.ElementTree import parse as xml_parse, ParseError as XMLParseError

logger = logging.getLogger(__name__)
Stencil = namedtuple("Stencil", ["id", "title", "width", "height", "path"])


class StencilRegistry:
    prefix = os.path.join("ui", "pkg", "stencils")
    # Replace missed stencil with Cisco | Router
    DEFAULT_STENCIL = "Cisco/router"
    DEFAULT_CLOUD_STENCIL = "Cisco/cloud"

    def __init__(self):
        self.choices = []
        self.stencils = {}  # id -> stencil

    @classmethod
    def stencil_from_svg(cls, path):
        """
        Read SVG and fetch metadata

        :param path:
        :return: Stencil insance or None in case of parsing error
        """
        # Get library path
        group = os.path.basename(os.path.dirname(path))
        file_name = os.path.basename(path)
        s_path = "%s/%s" % (group, file_name[:-4])
        # Parse SVG
        try:
            doc = xml_parse(path)
        except XMLParseError as e:
            logger.info("[%s] Cannot parse stencil: %s", s_path, e)
            return None
        svg = doc.getroot()
        # Get attributes
        # width
        width = svg.attrib.get("width")
        if not width:
            logger.info("[%s] Cannot parse stencil: <svg> tag contains no 'width' attribute", s_path)
            return None
        # height
        height = svg.attrib.get("height")
        if not height:
            logger.info("[%s] Cannot parse stencil: <svg> tag contains no 'height' attribute", s_path)
            return None
        # Get title from <title> tag
        title_el = svg.find("{http://www.w3.org/2000/svg}title")
        if title_el is None or title_el.text is None:
            title = None
        else:
            title = title_el.text.strip()
        if title:
            title = "%s | %s" % (group, title)
        else:
            logger.info("[%s] Missed <title> tag, generating title from file name", s_path)
            title = "%s | %s" % (group, os.path.basename(path)[:-4])
        # Build Stencil structure
        return Stencil(
            id=s_path,
            title=title,
            width=float(width),
            height=float(height),
            path=s_path
        )

    def load(self):
        for root, dirs, files in os.walk(self.prefix):
            for f in files:
                if not f.endswith(".svg"):
                    continue
                stencil = self.stencil_from_svg(os.path.join(root, f))
                if stencil:
                    self.stencils[stencil.id] = stencil
        self.choices = sorted(
            ((stencil_id, self.stencils[stencil_id].title)
             for stencil_id in self.stencils),
            key=itemgetter(1)
        )

    def get(self, stencil_id):
        """
        Get stencil instance by id
        :param stencil_id:
        :return: Stencil instance
        """
        stencil = self.stencils.get(stencil_id)
        if not stencil:
            stencil = self.stencils.get(self.DEFAULT_STENCIL)
        return stencil


stencil_registry = StencilRegistry()
stencil_registry.load()
