# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# gis.Overlay model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, DictField


class Overlay(Document):
    meta = {"collection": "noc.gis.overlays", "strict": False, "auto_create_index": False}

    name = StringField(required=True)
    gate_id = StringField(unique=True)
    is_active = BooleanField(required=True, default=True)
    permission_name = StringField(required=True)
    overlay = StringField(required=True)
    config = DictField()

    _overlay_cache = {}  # name -> Overlay

    def __str__(self):
        return self.name

    def get_overlay(self):
        if self.overlay not in self._overlay_cache:
            from noc.gis.overlays.base import OverlayHandler

            m = __import__("noc.gis.overlays.%s" % self.overlay, {}, {}, "*")
            for n in dir(m):
                o = getattr(m, n)
                if inspect.isclass(o) and o != OverlayHandler and issubclass(o, OverlayHandler):
                    self._overlay_cache[self.overlay] = o
                    break
        h = self._overlay_cache[self.overlay]
        return h(**self.config)
