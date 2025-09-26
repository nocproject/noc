# ---------------------------------------------------------------------
# Geocoding cache
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
import logging
import hashlib
import datetime
import codecs

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, FloatField, ListField, DateTimeField

# NOC modules
from noc.core.geocoder.base import GeoCoderResult
from noc.core.geocoder.errors import GeoCoderError
from noc.config import config
from noc.core.geocoder.loader import loader
from noc.core.comp import smart_bytes, smart_text

logger = logging.getLogger(__name__)


class GeocoderCache(Document):
    meta = {
        "collection": "noc.geocodercache",
        "indexes": [{"fields": ["expires"], "expireAfterSeconds": 0}],
    }

    # query hash
    hash = StringField(primary_key=True)
    # Raw query
    query = StringField()
    # Geocoding system
    geocoder = StringField()
    path = ListField(StringField())
    # Geo coordinates
    lon = FloatField()
    lat = FloatField()
    error = StringField()
    expires = DateTimeField()

    NEGATIVE_TTL = config.geocoding.negative_ttl

    rx_slash = re.compile(r"\s+/")
    rx_dots = re.compile(r"\.\.+")
    rx_sep = re.compile(r"[ \t;:!]+")
    rx_comma = re.compile(r"(\s*,)+")
    rx_dotcomma = re.compile(r",\s*\.,")

    geocoders = []

    @classmethod
    def iter_geocoders(cls):
        if not cls.geocoders:
            for gc in config.geocoding.order.split(","):
                gc = gc.strip()
                h = loader[gc]
                if h:
                    cls.geocoders += [h]
        yield from cls.geocoders

    @classmethod
    def clean_query(cls, query):
        query = smart_text(query)
        query = query.upper()
        query = cls.rx_slash.sub("/", query)
        query = cls.rx_dots.sub(" ", query)
        query = cls.rx_comma.sub(", ", query)
        query = cls.rx_dotcomma.sub(",", query)
        query = cls.rx_sep.sub(" ", query)
        return query.strip()

    @classmethod
    def get_hash(cls, query):
        return smart_text(codecs.encode(hashlib.sha256(smart_bytes(query)).digest(), "base64")[:12])

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
                lat=r.get("lat"),
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
                    r = None
                    error = "No coordinates"
                else:
                    if r and not lr and r.lon and r.lat:
                        lr = r  # Save first non-exact
                    r = None
            except GeoCoderError as e:
                error = str(e)
        sq = {"query": query, "system": gsys, "error": error}
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
        c.update_one({"_id": hash}, {"$set": sq}, upsert=True)
        return r
