# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Geocoding cache
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
import logging
import hashlib
import base64
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, FloatField, ListField,
                                DateTimeField)
# NOC modules
from noc.core.geocoding.base import GeoCoderError, GeoCoderResult
from noc.config import config
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)


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

    NEGATIVE_TTL = 7 * 86400

    rx_slash = re.compile(r"\s+/")
    rx_dots = re.compile(r"\.\.+")
    rx_sep = re.compile(r"[ \t;:!]+")
    rx_comma = re.compile("(\s*,)+")
    rx_dotcomma = re.compile(r",\s*\.,")

    geocoders = []

    gcls = {
        "yandex": "noc.core.geocoding.yandex.YandexGeocoder",
        "google": "noc.core.geocoding.google.GoogleGeocoder"
    }

    @classmethod
    def iter_geocoders(cls):
        if not cls.geocoders:
            for gc in config.geocoding.order.split(","):
                gc = gc.strip()
                if gc in cls.gcls:
                    h = get_handler(cls.gcls[gc])
                    if h:
                        cls.geocoders += [h]
        for h in cls.geocoders:
            yield h

    @classmethod
    def clean_query(cls, query):
        if type(query) == str:
            query = unicode(query, "utf-8")
        query = query.upper().encode("utf-8")
        query = cls.rx_slash.sub("/", query)
        query = cls.rx_dots.sub(" ", query)
        query = cls.rx_comma.sub(", ", query)
        query = cls.rx_dotcomma.sub(",", query)
        query = cls.rx_sep.sub(" ", query)
        return query.strip()

    @classmethod
    def get_hash(cls, query):
        return base64.b64encode(hashlib.sha256(query).digest())[:12]

    @classmethod
    def forward(cls, query, bounds=None):
        # Clean query
        query = cls.clean_query(query)
        if not query:
            logger.warning("Query is None")
            return None
        # Calculate hash
        hash = cls.get_hash(query)
        # Search data
        c = cls._get_collection()
        #
        r = c.find_one({"_id": hash})
        if r:
            # Found
            if r.get("error") and r.get("exact") is None:
                # If exact result - continue
                logger.warning("Error result and exact is NONE on query: %s", query)
                return None
            return GeoCoderResult(
                exact=r.get("exact", True),
                query=query,
                path=r.get("path") or [],
                lon=r.get("lon"),
                lat=r.get("lat")
            )
        # Not found, resolve
        r = None
        error = "Not found"
        gsys = None
        lr = None
        for gcls in cls.iter_geocoders():
            g = gcls()
            gsys = g.name
            try:
                r = g.forward(query, bounds)
                if r and r.exact:
                    if r.lon is not None and r.lat is not None:
                        error = None
                        break
                    else:
                        r = None
                        error = "No coordinates"
                else:
                    if r and not lr and r.lon and r.lat:
                        lr = r  # Save first non-exact
                    r = None
            except GeoCoderError as e:
                error = str(e)
        sq = {
            "query": query,
            "system": gsys,
            "error": error
        }
        if not r and lr:
            r = lr  # Reuse first non-exact message
        if r:
            if r.path:
                sq["path"] = r.path
            if r.lon and r.lat:
                sq["lon"], sq["lat"] = r.lon, r.lat
            sq["exact"] = r.exact
        if not r or not r.exact:
            sq["expires"] = datetime.datetime.now() + datetime.timedelta(seconds=cls.NEGATIVE_TTL)
        # Write to database
        c.update({
            "_id": hash
        }, {"$set": sq}, upsert=True)
        return r
