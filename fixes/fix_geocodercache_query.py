# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Convert legacy PoP links
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.gis.models.geocodercache import GeocoderCache


def fix():
    for o in GeocoderCache.objects.all():
        nq = GeocoderCache.clean_query(o.query)
        if nq != o.query:
            logging.info("%s -> %s", o.query, nq)
            GeocoderCache(
                hash=GeocoderCache.get_hash(nq),
                query=nq,
                geocoder=o.geocoder,
                path=o.path,
                lon=o.lon,
                lat=o.lat,
                error=o.error,
                expires=o.expires
            ).save()
            o.delete()
