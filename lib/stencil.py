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
        self.img_path = img_path
        self.name = name
        self.width = width
        self.height = height

    def get_stencil(self):
        return ("<shape name='%s' aspect='fixed' w='%s' h='%s'>" \
               "    <background>" \
               "        <image src='%s' w='%s' h='%s' />" \
               "</background>" \
               "<foreground></foreground>" \
               "</shape>") % (
            self.id, self.width, self.height, self.img_path,
            self.width, self.height
        )

class StencilRegistry:
    prefix = "static/shape/"
    manifest = "MANIFEST"

    def __init__(self):
        self.choices = []
        self.stencils = {}  # id -> stencil

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


stencil_registry = StencilRegistry()
stencil_registry.load()
