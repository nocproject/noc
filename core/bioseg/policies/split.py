# ----------------------------------------------------------------------
# Split Biosegmentation policy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Set

# NOC modules
from .base import BaseBioSegPolicy
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.link import Link


class SplitBioSegPolicy(BaseBioSegPolicy):
    """
    SPLIT Biosegmentation policy. Attacker looses targeted objects to new floating segment.
    """

    name = "split"
    PERSISTENT_POLICY = {
        "merge": "feed",
        "keep": "keep",
        "eat": "keep",
        "feed": "feed",
        "calcify": "calcify",
    }
    FLOATING_POLICY = {
        "merge": "merge",
        "keep": "keep",
        "eat": "eat",
        "feed": "feed",
        "calcify": "calcify",
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
            ns = NetworkSegment(
                name=f"Floating segment {mo.name}",
                parent=self.target,
                profile=self.calcified_profile,
            )
            ns.save()
            for mo in ManagedObject.objects.filter(id__in=objects):
                mo.segment = ns
                mo.save()
        return "split"

    def ensure_segment(self):
        """

        :return:
        """
        ...

    def get_linked_object(self, o: List[int]) -> List[int]:
        attacker_objects = {
            ManagedObject.objects.filter(is_managed=True, segment=self.attacker.id).values_list(
                "id", flat=True
            )
        }
        object_mos: Set[int] = set(o)
        while True:
            links = set()
            for o_links, o_level in ManagedObject.objects.filter(
                id__in=list(object_mos)
            ).values_list("links", "object_profile__level"):
                links |= o_links - attacker_objects
            if not set(links) - object_mos:
                break
        return list(object_mos)
