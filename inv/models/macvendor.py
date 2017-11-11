# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MAC Vendor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne, InsertOne, DeleteOne
# NOC modules
from noc.lib.nosql import Document, StringField

logger = logging.getLogger(__name__)


class MACVendor(Document):
    """
    IEEE OUI database
    """
    meta = {
        "collection": "noc.macvendors",
        "strict": False,
        "auto_create_index": False
    }

    # 3 octets, hexadecimal, upper
    oui = StringField(primary_key=True)
    vendor = StringField()

    DOWNLOAD_URL = "http://standards-oui.ieee.org/oui.txt"

    @classmethod
    def get_vendor(cls, mac):
        """
        Returns vendor for MAC or None
        """
        oui = mac.replace(":", "").upper()[:6]
        d = MACVendor._get_collection().find_one({
            "_id": oui
        }, {
            "_id": 0,
            "vendor": 1
        })
        if d:
            return d.get("vendor")
        else:
            return None

    @classmethod
    def update(cls):
        import requests
        # Get new values
        new = {}
        logger.info("Fetching new items from %s", cls.DOWNLOAD_URL)
        r = requests.get(cls.DOWNLOAD_URL)
        assert r.status_code == 200
        for l in r.text.splitlines():
            if "(hex)" in l:
                oui, vendor = l.split("(hex)")
                oui = oui.strip().replace("-", "").upper()
                vendor = vendor.strip()
                new[oui] = vendor
        # Get old values
        old = dict((d["_id"], d["vendor"])
                   for d in MACVendor._get_collection().find())
        # Compare
        collection = MACVendor._get_collection()
        bulk = []
        for oui, vendor in new.iteritems():
            if oui in old:
                if vendor != old[oui]:
                    logger.info("[%s] %s -> %s", oui, old[oui], vendor)
                    bulk += [UpdateOne({"_id": oui}, {"$set": {"vendor": vendor}})]
            else:
                logger.info("[%s] Add %s", oui, vendor)
                bulk += [InsertOne({"_id": oui, "vendor": vendor})]
        for oui in set(old) - set(new):
            logger.info("[%s] Delete")
            bulk += [DeleteOne({"_id": oui})]
        if bulk:
            logger.info("Commiting changes to database")
            try:
                r = collection.bulk_write(bulk)
                logger.info("Database has been synced")
                logger.info("Inserted: %d, Modify: %d, Deleted: %d",
                            r.inserted_count + r.upserted_count,
                            r.modified_count, r.deleted_count)
            except BulkWriteError as e:
                logger.error("Bulk write error: '%s'", e.details)
                logger.error("Stopping check")
