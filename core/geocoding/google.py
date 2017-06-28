# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Google geocoder
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urllib
## Third-party modules
import ujson
## NOC modules
from base import (BaseGeocoder, GeoCoderError, GeoCoderResult)
from noc.core.config.base import config


class GoogleGeocoder(BaseGeocoder):
    name = "google"

    def __init__(self, key=config.geocoding_google_key,
                 language=config.geocoding_google_language,
                 *args, **kwargs):
        super(GoogleGeocoder, self).__init__(*args, **kwargs)
        self.key = key
        self.language = language

    def forward(self, query, bounds=None, region=None):
        query = query.lower().strip()
        if not query:
            return None
        url = [
            "http://maps.googleapis.com/maps/api/geocode/json?"
        ]
        if region:
            url += ["&region=%s" % region]
        if bounds:
            # &bounds=34.172684,-118.604794|34.236144,-118.500938
            # bounds = ("34.172684,-118.604794", "34.236144,-118.500938")
            url += ["&bounds=%s|%s" % bounds]
        url += ["&address=%s" % urllib.quote(query)]
        if self.key:
            url += ["&key=%s" % urllib.quote(self.key)]
        if self.language:
            url += ["&language=%s" % urllib.quote(self.language)]
        code, response = self.get("".join(url))
        if code != 200:
            raise GeoCoderError("%s: %s" % (code, response))
        try:
            r = ujson.loads(response)
        except ValueError:
            raise GeoCoderError("Cannot decode result")
        if r["status"] != "OK":
            return None
        for rr in r["results"]:
            lon = self.get_path(rr, "geometry.location.lng")
            lat = self.get_path(rr, "geometry.location.lat")
            if not rr.get("address_components"):
                return None
            path = [x["short_name"] for x in rr["address_components"]]
            if "postal_code" in rr["address_components"][-1]["types"]:
                path = path[:-1]
            path.reverse()
            is_exact = self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.precision") == "exact"
            return GeoCoderResult(
                exact=is_exact,
                query=query,
                path=path,
                lon=lon,
                lat=lat
            )
