# ----------------------------------------------------------------------
# Yandex geocoder
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from urllib.parse import quote as urllib_quote
from typing import Optional

# Third-party modules
import orjson

# NOC modules
from .base import BaseGeocoder, GeoCoderResult
from .errors import GeoCoderError, GeoCoderLimitExceeded
from noc.config import config


class YandexGeocoder(BaseGeocoder):
    name = "yandex"

    def __init__(self, apikey: str, *args, **kwargs) -> str:
        super().__init__(*args, **kwargs)
        self.apikey = apikey or config.geocoding.yandex_apikey

    def forward(self, query: str, bounds=None, region=None) -> Optional[GeoCoderResult]:
        url = ["https://geocode-maps.yandex.ru/1.x/?", "format=json"]
        if region:
            url += [f"&region={region}"]
        if bounds:
            # "&rspn=1&bbox=127.56,49.96~141.05,56.09"
            url += ["&rspn=1", f"&bbox={bounds}~{bounds}"]
        url += [f"&geocode={urllib_quote(query)}"]
        if self.apikey:
            url += [f"&apikey={urllib_quote(self.apikey)}"]
        code, response = self.get("".join(url))
        if code == 429:
            raise GeoCoderLimitExceeded()
        if code != 200:
            raise GeoCoderError(f"{code}: {response}")
        try:
            r = orjson.loads(response)
        except ValueError:
            raise GeoCoderError("Cannot decode result")
        results = self.get_path(r, "response.GeoObjectCollection.featureMember") or []
        for rr in results:
            path = []
            pos = self.get_path(rr, "GeoObject.Point.pos")
            if pos:
                lon, lat = [float(x) for x in pos.split()]
            else:
                lon, lat = None, None
            for data in self.get_path(
                rr, "GeoObject.metaDataProperty.GeocoderMetaData.Address.Components"
            ):
                if data["name"] not in path:
                    path.append(data["name"])
            if path is None:
                break
            is_exact = (
                self.get_path(rr, "GeoObject.metaDataProperty.GeocoderMetaData.precision")
                == "exact"
            )
            if is_exact:
                return GeoCoderResult(
                    exact=is_exact,
                    query=query,
                    path=path,
                    lon=lon,
                    lat=lat,
                    id=None,
                    scope="yandex",
                    address=None,
                )
            return GeoCoderResult(
                exact=is_exact,
                query=query,
                path=path,
                lon=lon,
                lat=lat,
                id=None,
                scope="yandex",
                address=None,
            )
