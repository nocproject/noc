# ---------------------------------------------------------------------
# MAC Vendor
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from gufo.http import DEFLATE, GZIP
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne, InsertOne, DeleteOne
from mongoengine.document import Document
from mongoengine.fields import StringField

# NOC Modules
from noc.core.http.sync_client import HttpClient
from noc.config import config

logger = logging.getLogger(__name__)


class MACVendor(Document):
    """
    IEEE OUI database
    """

    meta = {"collection": "noc.macvendors", "strict": False, "auto_create_index": False}

    # 3 octets, hexadecimal, upper
    oui = StringField(primary_key=True)
    vendor = StringField()

    DOWNLOAD_URL = config.path.mac_vendor_url

    def __str__(self):
        return self.oui

    @classmethod
    def get_vendor(cls, mac):
        """
        Returns vendor for MAC or None
        """
        oui = mac.replace(":", "").upper()[:6]
        d = MACVendor._get_collection().find_one({"_id": oui}, {"_id": 0, "vendor": 1})
        if d:
            return d.get("vendor")
        else:
            return None

    @classmethod
    def update(cls):
        # Get new values
        new = {}
        logger.info("Fetching new items from %s", cls.DOWNLOAD_URL)
        client = HttpClient(
            max_redirects=1, compression=DEFLATE | GZIP, connect_timeout=10, validate_cert=False
        )
        status, h, content = client.get(cls.DOWNLOAD_URL)
        assert status == 200
        for l in content.decode().splitlines():
            if "(hex)" in l:
                oui, vendor = l.split("(hex)")
                oui = oui.strip().replace("-", "").upper()
                vendor = vendor.strip()
                new[oui] = vendor
        # Get old values
        old = {d["_id"]: d["vendor"] for d in MACVendor._get_collection().find()}
        # Compare
        collection = MACVendor._get_collection()
        bulk = []
        for oui, vendor in new.items():
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
                r = collection.bulk_write(bulk, ordered=False)
                logger.info("Database has been synced")
                if r.acknowledged:
                    logger.info(
                        "Inserted: %d, Modify: %d, Deleted: %d",
                        r.inserted_count + r.upserted_count,
                        r.modified_count,
                        r.deleted_count,
                    )
            except BulkWriteError as e:
                logger.error("Bulk write error: '%s'", e.details)
                logger.error("Stopping check")
