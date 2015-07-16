# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Stencil Registry
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import csv


class Stencil(object):
    def __init__(self, id, img_path, name, width, height):
        self.id = id
        self.name = name
        self.width = float(width)
        self.height = float(height)
        with open(img_path[1:]) as f:
            self.svg = f.read()

    def get_stencil(self, status):
        path = "/inv/map/stencils/%s/%s/" % (status, self.id)
        return ("<shape name='%s#%s' aspect='fixed' w='%s' h='%s'>"
               "    <background>"
               "        <image src='%s' w='%s' h='%s' />"
               "</background>"
               "<foreground></foreground>"
               "</shape>") % (
            self.id, status, self.width, self.height, path,
            self.width, self.height
        )

    def get_svg(self, color):
        return self.svg.replace("#000000", color)


class StencilRegistry:
    prefix = "static/shape/"
    manifest = "MANIFEST"

    COLOR_MAP = {
        "n": "#0892c3",
        "w": "#e8d0a9",
        "a": "#ff6600",
        "u": "#666666"
    }

    def __init__(self):
        self.choices = []
        self.stencils = {}  # id -> stencil
        self.svg = {}
        for n in self.COLOR_MAP:
            self.svg[n] = {}

    def load(self):
        for root, dirs, files in os.walk(self.prefix):
            if self.manifest in files:
                self.load_manifest(os.path.join(root, self.manifest))

    def load_manifest(self, path):
        d = os.path.dirname(path)[len(self.prefix):]
        with open(path) as f:
            reader = csv.reader(f)
            reader.next()
            for row in reader:
                if not row:
                    continue
                file, name, w, h = row
                n = os.path.splitext(file)[0]
                id = os.path.join(d, n)
                s = Stencil(
                    id=id,
                    img_path=os.path.join("/", self.prefix, d, file),
                    name=name,
                    width=w,
                    height=h
                )
                self.stencils[id] = s
                self.choices += [(id, name)]

    def get_svg(self, shape):
        st = self.stencils.get(shape)
        if not st:
            return None
        else:
            return st.svg

    def get_size(self, shape):
        """
        Returns width, height of shape
        """
        st = self.stencils.get(shape)
        if not st:
            return None, None
        else:
            return st.width, st.height


stencil_registry = StencilRegistry()
stencil_registry.load()
