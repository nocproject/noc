# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Geoconding cache
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


## Python modules
import re
import hashlib
import base64
import datetime
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, FloatField, ListField,
                                DateTimeField)
## NOC modules
from noc.core.geocoding.base import GeoCoderError, GeoCoderResult
from noc.core.geocoding.yandex import YandexGeocoder


class GeocoderCache(Document):
    meta = {
        "collection": "noc.geocodercache",
        "indexes": [
            {
                "fields": ["expires"],
                "expireAfterSeconds": 0
            }
        ]
    }

    # query hash
    hash = StringField(primary_key=True)
    # Raw query
    query = StringField()
    # Geocoding system
    geocoder = StringField()
    #
    path = ListField(StringField())
    # Geo coordinates
    lon = FloatField()
    lat = FloatField()
    #
    error = StringField()
    #
    expires = DateTimeField()

    NEGATIVE_TTL = 86400
    rx_sep = re.compile("[ \t;:]+")

    # @todo: Configurable order
    geocoders = [
        YandexGeocoder
    ]

    @classmethod
    def clean_query(cls, query):
        return cls.rx_sep.sub(" ", query.strip().upper()).strip()

    @classmethod
    def get_hash(cls, query):
        return base64.b64encode(hashlib.sha256(query).digest())[:12]

    @classmethod
    def forward(cls, query):
        # Clean query
        query = cls.clean_query(query)
        # Calculate hash
        hash = cls.get_hash(query)
        # Search data
        c = cls._get_collection()
        #
        r = c.find_one({"_id": hash})
        if r:
            # Found
            if r["error"]:
                return None
            return GeoCoderResult(
                exact=True,
                query=query,
                path=r.get("path") or [],
                lon=r.get("lon"),
                lat=r.get("lat")
            )
        # Not found, resolve
        r = None
        error = "Not found"
        gsys = None
        for gcls in cls.geocoders:
            g = gcls()
            gsys = g.name
            try:
                r = g.forward(query)
                if r.exact:
                    error = None
                    break
                else:
                    r = None
            except GeoCoderError as e:
                error = str(e)
        sq = {
            "query": query,
            "system": gsys,
            "error": error
        }
        if r:
            if r.path:
                sq["path"] = r.path
            if r.lon and r.lat:
                sq["lon"], sq["lat"] = r.lon, r.lat
        else:
            sq["expires"] = datetime.datetime.now() + datetime.timedelta(seconds=cls.NEGATIVE_TTL)
        # Write to database
        c.update({
            "_id": hash
        }, {"$set": sq}, upsert=True)
        return r
