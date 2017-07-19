# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Caps check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sla.models.slaprobe import SLAProbe, SLAProbeTest


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
        "Generic.Host": set()
    }

    def has_required_capabilities(self):
        if not super(SLACheck, self).has_required_capabilities():
            return False
        object_caps = self.object.get_caps()
        check_caps = self.PROFILE_CAPS.get(self.object.profile_name, set()) | self.PROFILE_CAPS["Generic.Host"]
        for c in object_caps:
            if c in check_caps and object_caps[c]:
                self.logger.info("Activated by '%s' capability", c)
                return True
        self.logger.info("Has no required capabilities. Skipping")
        return False

    def handler(self):
        self.logger.info("Checking SLA Probes")
        n = {}
        for p in self.object.scripts.get_sla_probes():
            n[p["name"]] = p
        # Check existing probes
        for p in SLAProbe.objects.filter(managed_object=self.object.id):
            if p.name not in n:
                self.logger.info("[%s] Removing probe", p.name)
                p.delete()
                continue
            changed = False
            nt = {}
            d = n[p.name].get("description")
            if p.description != d:
                self.logger.info(
                    "[%s] Changing description: %s -> %s",
                    p.name, p.description, d
                )
                p.description = d
                changed = True
            for t in n[p.name]["tests"]:
                nt[t["name"]] = t
            deleted = set()
            for t in p.tests:
                if t.name not in nt:
                    # Schedule test to remove
                    deleted.add(t.name)
                    continue
                nn = nt[t.name]
                for a in ("type", "target", "hw_timestamp"):
                    v = getattr(t, a)
                    if nn[a] != v:
                        self.logger.info(
                            "[%s|%s] Changing %s: %s -> %s",
                            p.name, t.name, a, v, nn[a]
                        )
                        setattr(t, a, nn[a])
                        changed = True
            if deleted:
                self.logger.info(
                    "[%s] Deleting tests: %s",
                    p.name, ", ".join(sorted(deleted))
                )
                p.tests = [t for t in p.tests if t.name not in deleted]
                changed = True
            if changed:
                p.save()
            del n[p.name]
        # Add left probes
        for p in six.itervalues(n):
            self.logger.info("Creating probe %s", p["name"])
            probe = SLAProbe(
                managed_object=self.object,
                name=p["name"],
                description=p.get("description"),
                tests=[
                    SLAProbeTest(name=t["name"],
                                 type=t["type"],
                                 target=t["target"],
                                 hw_timestamp=t["hw_timestamp"])
                    for t in p["tests"]
                ]
            )
            probe.save()
