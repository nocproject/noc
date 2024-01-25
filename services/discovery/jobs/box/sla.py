# ---------------------------------------------------------------------
# Caps check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sla.models.slaprobe import SLAProbe
from noc.sla.models.slaprofile import SLAProfile
from noc.core.profile.loader import GENERIC_PROFILE
from noc.main.models.label import Label


class SLACheck(DiscoveryCheck):
    """
    SLA discovery
    """

    name = "sla"
    required_script = "get_sla_probes"

    PROFILE_CAPS = {
        #
        "Cisco.IOS": {"Cisco | IP | SLA | Probes"},
        "Juniper.JUNOS": {"Juniper | RPM | Probes"},
        "Huawei.VRP": {"Huawei | NQA | Probes"},
        "OneAccess.TDRE": {"OneAccess | IP | SLA | Probes"},
        # Fallback
        GENERIC_PROFILE: set(),
    }

    def has_required_capabilities(self):
        if not super().has_required_capabilities():
            return False
        object_caps = self.object.get_caps()
        check_caps = (
            self.PROFILE_CAPS.get(self.object.profile.name, set())
            | self.PROFILE_CAPS[GENERIC_PROFILE]
        )
        for c in object_caps:
            if c in check_caps and object_caps[c]:
                self.logger.info("Activated by '%s' capability", c)
                return True
        self.logger.info("Has no required capabilities. Skipping")
        return False

    def handler(self):
        # Get configured probes
        self.logger.info("Checking SLA Probes")
        new_probes = {}
        for p in self.object.scripts.get_sla_probes():
            new_probes[p.get("group", ""), p["name"]] = p
            for ll in p.get("tags", []):
                Label.ensure_label(ll, ["sla.SLAProbe"])
        # Check existing probes
        for p in SLAProbe.objects.filter(managed_object=self.object.id):
            group = p.group or ""
            new_data = new_probes.get((group, p.name))
            if not new_data:
                # Remove stale probe
                self.logger.info("[%s|%s] Removing probe", group, p.name)
                p.fire_event("missed")
                continue
            extra_labels = set(p.extra_labels.get("sa", []))
            for ll in new_data.get("tags", []):
                if ll in extra_labels:
                    continue
                self.logger.info("[%s] Ensure SLA label: %s", p.id, ll)
                Label.ensure_label(ll, ["sla.SLAProbe"])
            self.update_if_changed(
                p,
                {
                    "description": new_data.get("description"),
                    "type": new_data["type"],
                    "tos": new_data.get("tos", 0),
                    "target": new_data["target"],
                    "hw_timestamp": new_data.get("hw_timestamp", False),
                    "extra_labels": [
                        ll for ll in new_data.get("tags", []) if SLAProbe.can_set_label(ll)
                    ],
                },
            )
            p.fire_event("seen")
            if not new_data["status"]:
                p.fire_event("down")
            else:
                p.fire_event("up")
            p.touch()
            del new_probes[group, p.name]
        # Add remaining probes
        for group, name in new_probes:
            self.logger.info("[%s|%s] Creating probe", group, name)
            new_data = new_probes.get((group, name))
            probe = SLAProbe(
                managed_object=self.object,
                name=name,
                profile=SLAProfile.get_default_profile(),
                group=group,
                description=new_data.get("description"),
                type=new_data["type"],
                tos=new_data.get("tos", 0),
                target=new_data["target"],
                hw_timestamp=new_data.get("hw_timestamp", False),
            )
            if new_data.get("tags"):
                probe.labels = [ll for ll in new_data["tags"] if SLAProbe.can_set_label(ll)]
                probe.extra_labels["sa"] = new_data["tags"]
            probe.save()
            if not new_data["status"]:
                probe.fire_event("down")

        self.update_caps(
            {"DB | SLAProbes": SLAProbe.objects.filter(managed_object=self.object.id).count()},
            source="sla",
        )
