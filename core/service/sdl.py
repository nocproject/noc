# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SDL Request handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
## Third-party modules
import tornado.web


class SDLRequestHandler(tornado.web.RequestHandler):
    def initialize(self, sdl):
        self.sdl = sdl

    def get(self):
        self.set_header("Content-Type", "text/javascript")
        self.write("var SDL = %s;" % json.dumps(self.sdl))
