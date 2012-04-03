# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## gis.tms application
## Tile Server
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from xml.dom.minidom import Document
## NOC modules
from noc.lib.fileutils import read_file
from noc.lib.app import ExtApplication, view
from noc.gis.models import TileCache, Map


class TMSApplication(ExtApplication):
    """
    gis.tms application:
    TMS-compliant server

    @todo: Cache control
    """

    TMS_VERSION = "1.0.0"

    def get_root(self, request):
        """
        Returns Full URL to service
        :rtype: str
        """
        return "http://%s/gis/tms/" % (request.META["HTTP_HOST"])

    @view(url=r"^$", method=["GET"], access="view", api=True)
    def api_services(self, request):
        """
        Render Services description XML
        """
        # @todo: proper protocol detection
        doc = Document()
        services = doc.createElement("Services")
        tmsv1 = doc.createElement("TileMapService")
        tmsv1.setAttribute("title", "TMS v1.0.0")
        tmsv1.setAttribute("version", self.TMS_VERSION)
        tmsv1.setAttribute("href", "%s%s/" % (self.get_root(request),
                                              self.TMS_VERSION))
        services.appendChild(tmsv1)
        doc.appendChild(services)
        return self.render_response(doc.toxml(), "text/xml")

    @view(url="^1.0.0/$", method=["GET"], access="view", api=True)
    def api_tms100(self, request):
        """
        Render TileMapService XML
        :param request:
        :return:
        """
        doc = Document()
        tmsv1 = doc.createElement("TileMapService")
        tmsv1.setAttribute("version", self.TMS_VERSION)
        tmsv1.setAttribute("services", self.get_root(request))
        # <Title>
        title = doc.createElement("Title")
        title.appendChild(doc.createTextNode("NOC Tile Map Service"))
        tmsv1.appendChild(title)
        # <Abstract>
        abstract = doc.createElement("Abstract")
        abstract.appendChild(doc.createTextNode("NOC Tile Map Service. "\
                                                "http://nocproject.org/"))
        tmsv1.appendChild(abstract)
        # <TileMaps>
        tilemaps = doc.createElement("TileMaps")
        root = self.get_root(request)
        for m in Map.objects.filter(is_active=True).order_by("name"):
            # <TileMap>
            tm = doc.createElement("TileMap")
            tm.setAttribute("title", m.name)
            tm.setAttribute("srs", m.srs.full_id)
            tm.setAttribute("profile", "local")
            tm.setAttribute("href", "%s%s/%s" % (root, self.TMS_VERSION, m.id))
            tilemaps.appendChild(tm)
        tmsv1.appendChild(tilemaps)
        doc.appendChild(tmsv1)
        return self.render_response(doc.toxml(), "text/xml")

    @view(url=r"^1.0.0/(?P<map>[0-9a-f]{24})/(?P<zoom>\d\d?)/(?P<x>\d+)/(?P<y>\d+).png",
          method=["GET"], url_name="tms_tile", access="view", api=True)
    def api_tms_tile(self, request, map, zoom, x, y):
        """
        Feed pre-rendered tile (with TMS Y-axis flip)

        @todo: caching
        :param request:
        :param map: Map ObjectId
        :param zoom: Zoom Level [0 .. 18]
        :param x: X tile index [0 .. 2 ** zoom )
        :param y: Y tile index [0 .. 2 ** zoom )
        :return:
        """
        zoom = int(zoom)
        if zoom < 0 or zoom > 18:
            return self.response_bad_request("Invalid zoom")
        m = 2 ** zoom
        x = int(x)
        y = m - 1 - int(y)   # Flip Y
        return self.render_tile(map, zoom, x, y)

    @view(url=r"^(?P<map>[0-9a-f]{24})/(?P<zoom>\d\d?)/(?P<x>\d+)/(?P<y>\d+).png",
          method=["GET"], url_name="tile", access="view", api=True)
    def api_tile(self, request, map, zoom, x, y):
        """
        Feed pre-rendered tile (XYZ-style)

        @todo: caching
        :param request:
        :param map: Map ObjectId
        :param zoom: Zoom Level [0 .. 18]
        :param x: X tile index [0 .. 2 ** zoom )
        :param y: Y tile index [0 .. 2 ** zoom )
        :return:
        """
        zoom = int(zoom)
        if zoom < 0 or zoom > 18:
            return self.response_bad_request("Invalid zoom")
        x = int(x)
        y = int(y)
        return self.render_tile(map, zoom, x, y)

    def render_tile(self, map, zoom, x, y):
        """
        Feed tile from tilecache
        :param map: Map ObjectId
        :param zoom: Zoom Level [0 .. 18]
        :param x: X tile index [0 .. 2 ** zoom )
        :param y: Y tile index [0 .. 2 ** zoom )
        :return:
        """
        def get_img(attr, path):
            try:
                return getattr(self, attr)
            except AttributeError:
                data = read_file(path)
                setattr(self, attr, data)
                return data

        m = 2 ** zoom
        if x < 0 or y < 0 or x >= m or y >= m:
            return self.response_bad_request("Invalid tile index")
        tc = TileCache.objects.filter(map=map, zoom=zoom, x=x, y=y).first()
        if tc:
            if tc.ready:
                data = tc.data
            else:
                data = get_img("img_not_ready", "static/img/gis/notready.png")
        else:
            data = get_img("img_no_data", "static/img/gis/nodata.png")
        return self.render_response(data, "image/png")
