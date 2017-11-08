# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Version check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware


class VersionCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "version"
    required_script = "get_version"

    def handler(self):
        self.logger.info("Checking version")
        result = self.object.scripts.get_version()
        changed = False
        # Sync vendor
        vendor = Vendor.ensure_vendor(result["vendor"])
        if not self.object.vendor or vendor.id != self.object.vendor.id:
            if self.object.vendor:
                self.logger.info("Vendor changed: %s -> %s",
                                 self.object.vendor.name, vendor.name)
            else:
                self.logger.info("Set vendor: %s", vendor.name)
            self.object.vendor = vendor
            changed = True
        # Sync platform
        platform = Platform.ensure_platform(vendor, result["platform"])
        if not self.object.platform or platform.id != self.object.platform.id:
            if self.object.platform:
                self.logger.info("Platform changed: %s -> %s",
                                 self.object.platform.name, platform.name)
            else:
                self.logger.info("Set platform: %s", platform.name)
            self.object.platform = platform
            changed = True
            # Platform changed, clear links
            self.clear_links()
        # Sync version
        version = Firmware.ensure_firmware(self.object.profile, vendor, result["version"])
        if not self.object.version or version.id != self.object.version.id:
            if self.object.version:
                self.logger.info("Version changed: %s -> %s",
                                 self.object.version.version,
                                 version.version)
            else:
                self.logger.info("Set version: %s", version.version)
            self.object.version = version
            changed = True
            # @todo: Check next_version and report upgrade
        # Sync image
        image = result.get("image")
        if image and image != self.object.software_image:
            image = image[:255]  # Cut to field length
            if self.object.version:
                self.logger.info("Image changed: %s -> %s",
                                 self.object.software_image, image)
            else:
                self.logger.info("Set image: %s", image)
            self.object.software_image = image
            changed = True
        # Sync attributes
        if "attributes" in result:
            self.object.update_attributes(result["attributes"])
        #
        if changed:
            self.object.save()
