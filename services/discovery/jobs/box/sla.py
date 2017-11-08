# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Caps check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
from noc.core.profile.loader import GENERIC_PROFILE
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sla.models.slaprobe import SLAProbe


class SLACheck(DiscoveryCheck):
    """
    SLA discovery
    """
    name = "sla"
    required_script = "get_sla_probes"

    PROFILE_CAPS = {
        #
        "Cisco.IOS": set([
            "Cisco | IP | SLA | Probes"
        ]),
        "Juniper.JUNOS": set([
            "Juniper | RPM | Probes"
        ]),
        "OneAccess.TDRE": set([
            "OneAccess | IP | SLA | Probes"
        ]),
        # Fallback
        GENERIC_PROFILE: set()
    }

    def has_required_capabilities(self):
        if not super(SLACheck, self).has_required_capabilities():
            return False
        object_caps = self.object.get_caps()
        check_caps = self.PROFILE_CAPS.get(self.object.profile.name, set()) | self.PROFILE_CAPS[GENERIC_PROFILE]
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
        # Check existing probes
        for p in SLAProbe.objects.filter(managed_object=self.object.id):
            group = p.group or ""
            new_data = new_probes.get((group, p.name))
            if not new_data:
                # Remove stale probe
                self.logger.info("[%s|%s] Removing probe", group, p.name)
                p.delete()
                continue
            self.update_if_changed(p, {
                "description": new_data.get("description"),
                "type": new_data["type"],
                "target": new_data["target"],
                "hw_timestamp": new_data.get("hw_timestamp", False),
                "tags": new_data.get("tags", [])
            })
            del new_probes[group, p.name]
        # Add remaining probes
        for group, name in six.iterkeys(new_probes):
            self.logger.info("[%s|%s] Creating probe", group, name)
            new_data = new_probes.get((group, name))
            probe = SLAProbe(
                managed_object=self.object,
                name=name,
                group=group,
                description=new_data.get("description"),
                type=new_data["type"],
                target=new_data["target"],
                hw_timestamp=new_data.get("hw_timestamp", False),
                tags=new_data.get("tags", [])
            )
            probe.save()
