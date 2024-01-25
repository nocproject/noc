# ---------------------------------------------------------------------
# CPE check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any

# Third-party modules
from mongoengine.queryset.visitor import Q as m_Q

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.inv.models.cpe import CPE, ControllerItem
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
        processed = set()
        bulk = []
        for r in result:
            cpe = self.ensure_cpe(
                r["id"], r["global_id"], c_type=r["type"], interface=r.get("interface")
            )
            cpe.seen(self.object, r["id"], r.get("interface"), r["status"] == "active")
            # Change controller ? Log changes
            # cpe_cache[cpe.id] = cpe
            processed.add(cpe.id)
            # State
            if cpe.controller and cpe.controller.managed_object.id == self.object.id:
                cpe.fire_event("up", bulk=bulk)
            else:
                # For down CPE data is not updated
                cpe.fire_event("down", bulk=bulk)
                continue
            # ? multiple active
            if cpe.description != r.get("description"):
                cpe.description = r.get("description")
            if cpe.label != r.get("name"):
                cpe.label = r.get("name")
            # Update labels
            labels = r.get("labels")
            if labels is not None:
                for ll in labels:
                    Label.ensure_label(ll, ["inv.CPE"])
                cpe.labels = [ll for ll in labels if CPE.can_set_label(ll)]
                cpe.extra_labels = {"sa": cpe.labels}
            # Update Caps
            caps = self.cleanup_caps(r)
            cpe.update_caps(caps, source="cpe", scope="cpe")
            # Sync Address
            if cpe.address != r.get("ip"):
                cpe.address = r.get("ip")
            cpe.save()
            # Profile classification
            # Sync ManagedObject
            if cpe.profile.sync_managedobject:
                self.submit_managed_object(cpe)
        if bulk:
            CPE._get_collection().bulk_write(bulk)
        # Remove Unseen
        unseen_cpe_ids = (
            set(CPE.objects.filter(controllers__managed_object=self.object.id).values_list("id"))
            - processed
        )
        if unseen_cpe_ids:
            self.logger.info("%s CPE not seen", len(unseen_cpe_ids))
            for cpe in CPE.objects.filter(id__in=list(unseen_cpe_ids)):
                cpe.unseen(self.object)
        self.update_caps(
            {"DB | CPEs": CPE.objects.filter(controllers__managed_object=self.object.id).count()},
            source="cpe",
        )

    def submit_managed_object(self, cpe: CPE):
        """
        Create ManagedObject for CPE instance
        :param cpe:
        :return:
        """
        from django.db.models.query_utils import Q

        name = cpe.label or f"CPE-{cpe.type.upper()}-{cpe.global_id}"

        mo = ManagedObject.objects.filter(Q(cpe_id=str(cpe.id)) | Q(name=name)).first()
        if mo and not mo.cpe_id:
            # Old CPE, bind to current
            mo.cpe_id = str(cpe.id)
            mo.save()
        elif mo and not cpe.address:
            self.logger.info(
                "[%s] CPE Reset address. Change ManagedObject to inactive state",
                cpe.global_id,
            )
            mo.fire_event("unmanaged")
            mo.save()
            return
        elif not cpe.address:
            return
        elif mo and mo.address != cpe.address:
            self.logger.info(
                "[%s] Changed ManagedObject Address: %s -> %s",
                cpe.global_id,
                mo.address,
                cpe.address,
            )
            mo.address = cpe.address
            mo.save()
            mo.fire_event("seen")
            return
        elif mo:
            mo.fire_event("seen")
            return
        # Create ManagedObject
        self.logger.info("[%s] Created ManagedObject %s", cpe.global_id, name)
        mo = ManagedObject(
            name=name,
            pool=cpe.profile.object_pool or self.object.pool,
            profile=Profile.get_by_id(Profile.get_generic_profile_id()),
            object_profile=cpe.profile.object_profile or self.object.object_profile,
            administrative_domain=self.object.administrative_domain,
            scheme=cpe.controller.managed_object.scheme,
            segment=cpe.controller.managed_object.segment,
            auth_profile=None,
            address=cpe.address or "0.0.0.0",
            controller=cpe.controller.managed_object,
            cpe_id=str(cpe.id),
            bi_id=cpe.bi_id,
        )
        mo.save()

    def ensure_cpe(
        self,
        local_id: str,
        global_id: str,
        c_type: str,
        interface: Optional[str] = None,
    ) -> CPE:
        """
        Ensure CPE exists and create it if not
        :param local_id: CPE id on controller
        :param global_id: CPE global_id (Serial or MAC)
        :param c_type: cpe type
        :param interface: Controller interface
        :return:
        """
        cpe = CPE.objects.filter(
            m_Q(global_id=global_id)
            | m_Q(controllers__match={"managed_object": self.object.id, "local_id": local_id})
        ).first()
        if cpe:
            return cpe
        self.logger.info("[%s|%s] Creating new cpe", global_id, local_id)
        cpe = CPE(
            profile=CPEProfile.get_default_profile(),
            controllers=[
                ControllerItem(
                    managed_object=self.object,
                    local_id=local_id,
                    interface=interface,
                )
            ],
            type=c_type,
            global_id=global_id,
        )
        cpe.save()
        return cpe

    def cleanup_caps(self, result: Dict[str, Any]) -> Dict[str, str]:
        r = {}
        for attr_name, caps in self.caps_map.items():
            if attr_name in result and result[attr_name]:
                r[caps] = result[attr_name]
        return r
