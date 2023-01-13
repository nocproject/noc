# ----------------------------------------------------------------------
# Split Biosegmentation policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Set, Dict, Any

# NOC modules
from .base import BaseBioSegPolicy
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.core.text import alnum_key


class SplitBioSegPolicy(BaseBioSegPolicy):
    """
    SPLIT Biosegmentation policy. Attacker looses targeted objects to new floating segment.
    """

    name = "split"
    PERSISTENT_POLICY = {
        "merge": "split",
        "keep": "split",
        "eat": "split",
        "feed": "split",
        "calcify": "calcify",
        "split": "split",
    }  # Attacker -> Target
    FLOATING_POLICY = {
        "merge": "keep",
        "keep": "split",
        "eat": "eat",
        "feed": "feed",
        "calcify": "calcify",
        "split": "split",
    }

    def trial(self) -> str:
        """
        1. Getting objects for split
        2. Create new segment
        3. Move objects to new segment
        :return:
        """
        self.logger.info("Applying %s policy", self.name)
        # Getting objects
        for link in Link.objects.filter(linked_segments__all=[self.attacker.id, self.target.id]):
            objects = self.get_linked_object(link.linked_objects)
            self.logger.info("Change segment on objects: %s", objects)
            mos = list(ManagedObject.objects.filter(id__in=objects))
            if not mos:
                continue
            if not self.calcified_profile:
                self.logger.info("Cannot split without calcified profile")
                raise ValueError("Cannot split without calcified profile")
            name = f"Floating segment {mos[0].name}"
            self.logger.info("Calcified profile: %s", self.calcified_profile)
            if self.calcified_profile.calcified_name_template:
                name = self.calcified_profile.calcified_name_template.render_body(
                    **self.get_template_context(link)
                )
            ns = NetworkSegment.objects.filter(name=name).first()
            if not ns:
                ns = NetworkSegment(
                    name=name,
                    parent=self.attacker,
                    profile=self.calcified_profile,
                )
                ns.save()
            for mo in mos:
                mo.segment = ns
                mo.save()
        return "split"

    def ensure_segment(self):
        """

        :return:
        """
        ...

    def get_linked_object(self, o: List[int]) -> List[int]:
        """
        Getting linked object chain inside attacker segment
        :param o:
        :return:
        """
        attacker_objects = set(
            ManagedObject.objects.filter(is_managed=True, segment=str(self.target.id)).values_list(
                "id", flat=True
            )
        )
        object_mos: Set[int] = set(o).intersection(attacker_objects)
        while True:
            links = set()
            for o_links, o_level in ManagedObject.objects.filter(
                id__in=list(object_mos)
            ).values_list("links", "object_profile__level"):
                links = set(o_links).intersection(attacker_objects)
            if not set(links) - object_mos:
                break
            object_mos |= links
        return list(object_mos)

    def get_template_context(self, link) -> Dict[str, Any]:
        local_interfaces: List[Interface] = []
        remote_interfaces: List[Interface] = []
        for iface in link.interfaces:
            if iface.managed_object.segment.id == self.attacker.id:
                local_interfaces += [iface]
            else:
                remote_interfaces += [iface]
        return {
            "interfaces": list(sorted(local_interfaces, key=lambda x: alnum_key(x.name))),
            "parent_interfaces": list(sorted(remote_interfaces, key=lambda x: alnum_key(x.name))),
            "attacker": self.attacker,
            "target": self.target,
        }
