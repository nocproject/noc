# ----------------------------------------------------------------------
# OSM Nominatim Geocoder
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from urllib.parse import quote as urllib_quote
from typing import Iterator

# Third-party modules
import orjson

# NOC modules
from .base import BaseGeocoder, GeoCoderResult
from .errors import GeoCoderError


class OSMNominatimGeocoder(BaseGeocoder):
    name = "osm"

    def iter_query(self, query: str, bounds=None) -> Iterator[GeoCoderResult]:
        q = urllib_quote(query)
        url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&addressdetails=1"
        if bounds:
            url += "viewbox=%s,%s" % bounds
        code, response = self.get("".join(url))
        if code != 200:
            raise GeoCoderError("%s: %s" % (code, response))
        try:
            r = orjson.loads(response)
        except ValueError:
            raise GeoCoderError("Cannot decode result")
        for x in r:
            osm_cls = x.get("class")
            yield GeoCoderResult(
                exact=osm_cls == "building",
                query=query,
                path=[],
                lon=self.maybe_float(x["lon"]),
                lat=self.maybe_float(x["lat"]),
                id=str(x["place_id"]),
                scope="osm",
                address=x["display_name"],
            )
