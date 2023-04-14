# ---------------------------------------------------------------------
# Version check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.inv.models.firmwarepolicy import FirmwarePolicy, FS_DENIED
from noc.core.wf.diagnostic import SNMPTRAP_DIAG, SYSLOG_DIAG


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
                self.logger.info("Vendor changed: %s -> %s", self.object.vendor.name, vendor.name)
            else:
                self.logger.info("Set vendor: %s", vendor.name)
            self.object.vendor = vendor
            changed = True
        # Sync platform
        strict_platform = self.object.object_profile.new_platform_creation_policy != "C"
        platform = Platform.ensure_platform(vendor, result["platform"], strict=strict_platform)
        if strict_platform and platform is None:
            # Denied to create platform, stop
            if self.object.object_profile.new_platform_creation_policy == "A":
                self.set_problem(
                    alarm_class="NOC | Managed Object | New Platform",
                    message=f'New platform ({vendor}: {result["platform"]}) creation is denied by policy',
                    fatal=True,
                )
            else:
                self.job.set_fatal_error()
            return
        if not self.object.platform or platform.id != self.object.platform.id:
            if self.object.platform:
                self.logger.info(
                    "Platform changed: %s -> %s", self.object.platform.name, platform.name
                )
            else:
                self.logger.info("Set platform: %s", platform.name)
            self.object.platform = platform
            changed = True
            # Platform changed, clear links
            if self.object.object_profile.clear_links_on_platform_change:
                self.clear_links()
            # Invalidate neighbor cache
            self.invalidate_neighbor_cache()
            # Reset diagnostics
            self.object.diagnostic.reset_diagnostics([SNMPTRAP_DIAG, SYSLOG_DIAG])
        # Sync version
        version = Firmware.ensure_firmware(self.object.profile, vendor, result["version"])
        if not self.object.version or version.id != self.object.version.id:
            if self.object.version:
                self.logger.info(
                    "Version changed: %s -> %s", self.object.version.version, version.version
                )
            else:
                self.logger.info("Set version: %s", version.version)
            self.object.event(
                self.object.EV_VERSION_CHANGED,
                {"current": str(version), "prev": str(self.object.version or "")},
            )
            self.object.version = version
            changed = True
            # @todo: Check next_version and report upgrade
        # Sync image
        image = result.get("image", "") or None
        if image != self.object.software_image:
            if image:
                image = image.strip()[:255]  # Cut to field length
            if not image:
                image = None
            if self.object.version:
                self.logger.info("Image changed: %s -> %s", self.object.software_image, image)
            else:
                self.logger.info("Set image: %s", image)
            self.object.software_image = image
            changed = True
        # Sync attributes
        if "attributes" in result:
            self.object.update_attributes(result["attributes"])
            self.set_artefact("object_attributes", result["attributes"])
        else:
            # Clear capabilities by attributes
            self.set_artefact("object_attributes", {})
        #
        if changed:
            self.object.save()
        #
        dfp = self.object.get_denied_firmware_policy()
        if dfp != "I":
            firmware_status = FirmwarePolicy.get_status(version, platform)
            if firmware_status == FS_DENIED:
                self.logger.info("Firmware version is denied by policy")
                if dfp in ("A", "S"):
                    self.set_problem(
                        alarm_class="NOC | Managed Object | Denied Firmware",
                        message="Firmware version is denied to use by policy",
                        fatal=dfp == "S",
                    )
                elif dfp == "s":
                    self.job.set_fatal_error()
                if dfp in ("s", "S"):
                    self.logger.error("Further box discovery is stopped by policy")
