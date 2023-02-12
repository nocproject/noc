# ---------------------------------------------------------------------
# CPE check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.inv.models.cpe import CPE
from noc.inv.models.cpeprofile import CPEProfile
from noc.main.models.label import Label


class CPECheck(DiscoveryCheck):
    """
    CPE check
    @todo: Remove stale CPE
    """

    name = "cpe"
    required_script = "get_cpe"
    # required_capabilities = ["CPE | Controller"]
    caps_map = {
        "vendor": "CPE | Vendor",
        "model": "CPE | Model",
        "version": "CPE | SW Version",
        "serial": "CPE | Serial Number",
        "mac": "CPE | MAC Address",
        "modulation": "CPE | Modulation",
        "location": "CPE | Location",
        "distance": "CPE | Distance",
    }

    def handler(self):
        self.logger.info("Checking CPEs")
        result = self.object.scripts.get_cpe()
        cpe_cache = {}
        assets_sync = []
        bulk = []
        for r in result:
            cpe = self.find_cpe(r["id"], r["global_id"])
            if not cpe:
                cpe = self.submit_cpe(
                    local_id=r["id"],
                    global_id=r["global_id"],
                    c_type=r["type"],
                    status=r["status"],
                    labels=r.get("labels"),
                    interface=r.get("interface"),
                    description=r.get("description"),
                )
            # Change controller ? Log changes
            cpe_cache[cpe.id] = cpe
            # Update Caps
            caps = self.cleanup_caps(r)
            cpe.update_caps(caps, source="cpe", scope="cpe")
            # Update labels
            # ifindex
            # State
            if r["status"] == "active":
                cpe.fire_event("up", bulk=bulk)
            else:
                cpe.fire_event("down", bulk=bulk)
            if cpe.profile.sync_asset and caps.get("CPE | Model"):
                assets_sync += [
                    (
                        caps.get("CPE | Vendor"),
                        caps.get("CPE | Model"),
                        caps.get("CPE | Serial Number"),
                    )
                ]
            # Sync ManagedObject
            if cpe.profile.sync_managedobject:
                self.submit_managed_object(cpe)
        if bulk:
            CPE._get_collection().bulk_write(bulk)
        # Sync Asset
        if assets_sync:
            self.set_artefact("cpe_objects", assets_sync)
        self.update_caps(
            {"DB | CPEs": CPE.objects.filter(controller=self.object.id).count()},
            source="cpe",
        )
        # Remove Unseen

    def submit_managed_object(self, cpe: CPE):
        """
        Create ManagedObject for CPE instance
        :param cpe:
        :return:
        """
        name = cpe.get("name") or "cpe-%s" % cpe["global_id"]
        if ManagedObject.objects.filter(name=name).exists():
            name = f"cpe-{cpe.global_id}"
        self.logger.info("[%s|%s] Created ManagedObject %s", cpe.local_id, cpe.global_id, name)
        mo = ManagedObject(
            name=name,
            pool=self.object.pool,
            profile=Profile.get_by_id(Profile.get_generic_profile_id()),
            object_profile=cpe.profile.object_profile or self.object.object_profile,
            administrative_domain=self.object.administrative_domain,
            scheme=self.object.scheme,
            segment=self.object.segment,
            auth_profile=self.object.object_profile.cpe_auth_profile or self.object.auth_profile,
            address=cpe.address or "0.0.0.0",
            controller=self.object,
            cpe_id=str(cpe.id),
            bi_id=cpe.bi_id,
        )
        mo.save()

    def submit_cpe(
        self,
        local_id: str,
        global_id: str,
        c_type: str,
        status: str,
        labels: Optional[List[str]] = None,
        interface: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> CPE:
        self.logger.info("[%s|%s] Creating new cpe", global_id, local_id)
        cpe = CPE(
            profile=CPEProfile.get_default_profile(),
            controller=self.object,
            type=c_type,
            local_id=local_id,
            global_id=global_id,
            description=description,
            interface=interface,
        )
        if labels is not None:
            for ll in labels:
                Label.ensure_label(ll)
            cpe.labels = [ll for ll in labels if CPE.can_set_label(ll)]
            cpe.extra_labels = {"sa": cpe.labels}
        cpe.save()
        cpe.fire_event("seen")
        return cpe

    def cleanup_caps(self, result: Dict[str, Any]) -> Dict[str, str]:
        r = {}
        for attr_name, caps in self.caps_map.items():
            if attr_name in result:
                r[caps] = result[attr_name]
        return r

    def find_cpe(self, global_id, local_id) -> Optional[CPE]:
        cpe = CPE.objects.filter(global_id=global_id).first()
        if not cpe:
            # ?Generate global_id
            cpe = CPE.objects.filter(controller=self.object.id, local_id=local_id).first()
        return cpe
