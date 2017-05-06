# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Yandex geocoder
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urllib
## Third-party modules
import ujson
## NOC modules
from base import (BaseGeocoder, GeoCoderError, GeoCoderLimitExceeded,
                  GeoCoderResult)
from noc.core.config.base import config


class YandexGeocoder(BaseGeocoder):
    name = "yandex"

    def __init__(self, key=config.geocoding_yandex_key,
                 apikey=None, *args, **kwargs):
        super(BaseGeocoder, self).__init__(*args, **kwargs)
        self.key = key
        self.apikey = apikey

    def forward(self, query, bounds=None, region=None):
        url = [
            "https://geocode-maps.yandex.ru/1.x/?",
            "format=json",

        ]
        if region:
            url += ["&region=%s" % region]
        if bounds:
            # "&rspn=1&bbox=127.56,49.96~141.05,56.09"
            url += ["&rspn=1",
                    "&bbox=%s~%s" % bounds]
        url += ["&geocode=%s" % urllib.quote(query)]
        if self.key:
            url += [
                "&key=%s" % urllib.quote(self.key)
            ]
        if self.apikey:
            url += [
                "&apikey=%s" % urllib.quote(self.apikey)
            ]
        code, response = self.get("".join(url))
        if code == 429:
            raise GeoCoderLimitExceeded()
        elif code != 200:
            raise GeoCoderError("%s: %s" % (code, response))
        try:
            r = ujson.loads(response)
        except ValueError:
            raise GeoCoderError("Cannot decode result")
        results = self.get_path(r, "response.GeoObjectCollection.featureMember") or []
        for rr in results:
            pos = self.get_path(rr, "GeoObject.Point.pos")
            if pos:
                lon, lat = [float(x) for x in pos.split()]
            else:
                lon, lat = None, None
            path = [
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.AddressDetails.Country.CountryName"),
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.AddressDetails.Country.AdministrativeArea.AdministrativeAreaName"),
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.SubAdministrativeAreaName"),
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.LocalityName"),
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.Thoroughfare.ThoroughfareName"),
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.Thoroughfare.Premise.PremiseNumber")
            ]
            path = [p for p in path if p]
            is_exact = self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.precision") == "exact"
            return GeoCoderResult(
                exact=is_exact,
                query=query,
                path=path,
                lon=lon,
                lat=lat
            )
