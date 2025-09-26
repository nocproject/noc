# ----------------------------------------------------------------------
# managedobject platform
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid

# Third-party modules
import bson
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.model.fields import DocumentReferenceField


class Migration(BaseMigration):
    def migrate(self):
        #
        # Platform and version
        #
        pcoll = self.mongo_db["noc.platforms"]
        fcoll = self.mongo_db["noc.firmwares"]

        data = self.db.execute(
            """
          SELECT
            DISTINCT
            mo.profile AS profile,
            mo.vendor AS vendor,
            a2.value AS platform,
            a3.value AS version
          FROM
            sa_managedobject mo
            JOIN sa_managedobjectattribute a2 ON (mo.id = a2.managed_object_id)
            JOIN sa_managedobjectattribute a3 ON (mo.id = a3.managed_object_id)
          WHERE
            a2.key = 'platform'
            AND a3.key = 'version'
        """
        )
        platforms = set()  # vendor, platform
        platforms_uniq = set()  # Uniq platform name
        versions = set()  # profile, version
        for profile, vendor, platform, version in data:
            platform = platform.strip() if platform and platform != "None" else None
            vendor = vendor.strip() if vendor and vendor != "None" else None
            if not platform or not vendor:
                continue
            if platform not in platforms_uniq:
                platforms.add((vendor, platform))
            versions.add((profile, vendor, version))
            platforms_uniq.add(platform)
        # Create platforms
        for vendor, platform in platforms:
            u = uuid.uuid4()
            v = bson.ObjectId(vendor)
            pcoll.update_one(
                {"vendor": v, "name": platform},
                {
                    "$set": {"name": platform, "full_name": platform},
                    "$setOnInsert": {"vendor": v, "uuid": u},
                },
                upsert=True,
            )
        # Create firmware
        for profile, vendor, version in versions:
            u = uuid.uuid4()
            pv = bson.ObjectId(profile)
            vv = bson.ObjectId(vendor)
            fcoll.update_one(
                {"profile": pv, "vendor": vv, "version": version},
                {
                    "$set": {"version": version},
                    "$setOnInsert": {"profile": pv, "vendor": vv, "uuid": u},
                },
                upsert=True,
            )
        # Get platforms records
        pmap = {}  # vendor, platform -> id
        for d in pcoll.find({}, {"_id": 1, "vendor": 1, "name": 1}):
            pmap[str(d["vendor"]), d["name"]] = str(d["_id"])
        # Get version records
        fmap = {}  # vendor, platform -> id
        for d in fcoll.find({}, {"_id": 1, "profile": 1, "version": 1}):
            fmap[str(d["profile"]), d["version"]] = str(d["_id"])
        # Create .platform field
        self.db.add_column(
            "sa_managedobject",
            "platform",
            DocumentReferenceField("inv.Platform", null=True, blank=True),
        )
        # Create .version field
        self.db.add_column(
            "sa_managedobject",
            "version",
            DocumentReferenceField("inv.Firmware", null=True, blank=True),
        )
        # Create .next_version field
        self.db.add_column(
            "sa_managedobject",
            "next_version",
            DocumentReferenceField("inv.Firmware", null=True, blank=True),
        )
        # Create software_image field
        self.db.add_column(
            "sa_managedobject",
            "software_image",
            models.CharField("Software Image", max_length=255, null=True, blank=True),
        )
        platforms_uniq = set()  # Uniq platform name
        for profile, vendor, platform, version in data:
            platform = platform.strip() if platform and platform != "None" else None
            vendor = vendor.strip() if vendor and vendor != "None" else None
            if not platform or not vendor:
                continue
            if (vendor, platform) not in pmap:
                continue
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET
                  platform = %s,
                  version = %s
                WHERE
                  id IN (
                    SELECT mo.id
                    FROM
                      sa_managedobject mo
                      JOIN sa_managedobjectattribute a2 ON (a2.managed_object_id = mo.id)
                      JOIN sa_managedobjectattribute a3 ON (a3.managed_object_id = mo.id)
                    WHERE
                      mo.profile = %s
                      AND mo.vendor = %s
                      AND a2.key = 'platform'
                      AND a2.value = %s
                      AND a3.key = 'version'
                      AND a3.value = %s
                  )
            """,
                [
                    pmap[vendor, platform],
                    fmap[profile, version],
                    profile,
                    vendor,
                    platform,
                    version,
                ],
            )
        # Fill software_image field
        images = self.db.execute(
            "SELECT DISTINCT value FROM sa_managedobjectattribute WHERE key='image'"
        )
        for (img,) in images:
            self.db.execute(
                """
            UPDATE sa_managedobject
            SET software_image = %s
            WHERE
              id IN (
                SELECT managed_object_id
                FROM sa_managedobjectattribute
                WHERE
                  key = 'image'
                  AND value = %s
                )
            """,
                [img, img],
            )
        # Remove old data
        self.db.execute(
            """
          DELETE FROM sa_managedobjectattribute
          WHERE key IN ('vendor', 'platform', 'version', 'image')
        """
        )
