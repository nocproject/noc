# ---------------------------------------------------------------------
# Rebuild pop links
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.interface import Interface
from noc.gis.models.layer import Layer
from noc.inv.models.link import Link

logger = logging.getLogger(__name__)


class LinkedPoP(object):
    def __init__(self, pop_id):
        self.pop = Object.get_by_id(pop_id)

    def iter_db_links(self, level):
        """
        Yield remote pop, layer
        """
        for c, remote, _ in self.pop.get_genderless_connections("links"):
            remote_level = remote.get_data("pop", "level")
            if not remote_level:
                logger.error("[%s|%s] Object has not PoP level. Skipping", remote.id, remote)
                continue
            layer = "pop_links%d" % (min(level, remote_level) // 10)
            yield c, remote, layer

    def get_pop_objects(self, root=None):
        """
        Get managed objects inside PoP
        """
        if not root:
            root = self.pop
        mos = set()
        for o in root.iter_children():
            if o.get_data("management", "managed"):
                # Managed object
                mo = o.get_data("management", "managed_object")
                if mo:
                    mos.add(mo)
            if o.get_data("container", "container"):
                mos |= self.get_pop_objects(o)
        return mos

    def get_linked_pops(self):
        linked = set()
        self.pops = set(self.get_pop_objects())
        self_interfaces = set(
            Interface.objects.filter(managed_object__in=self.pops).values_list("id")
        )
        r_ifaces = set()
        for ld in Link._get_collection().find(
            {"interfaces": {"$in": list(self_interfaces)}}, {"_id": 0, "interfaces": 1}
        ):
            r_ifaces |= set(ld.get("interfaces", []))
        r_ifaces -= self_interfaces
        r_mos = set(
            i["managed_object"]
            for i in Interface._get_collection().find(
                {"_id": {"$in": list(r_ifaces)}}, {"_id": 0, "managed_object": 1}
            )
        )
        for o in Object.objects.filter(
            data__match={
                "interface": "management",
                "attr": "managed_object",
                "value__in": list(r_mos),
            }
        ):
            pop = o.get_pop()
            if pop:
                linked.add(pop)
        return linked

    def update_links(self):
        if not self.pop:
            return
        level = self.pop.get_data("pop", "level")
        linked = self.get_linked_pops()
        for c, pop, layer in self.iter_db_links(level):
            if pop in linked:
                # Already linked
                if c.layer.code != layer:
                    logger.info(
                        "%s - %s. Changing link layer from %s to %s",
                        self.pop,
                        pop,
                        c.layer.code,
                        layer,
                    )
                    c.layer = Layer.get_by_code(layer)
                linked.remove(pop)
            else:
                # Unlink
                logger.info("Unlinking %s - %s", self.pop, pop)
                c.delete()
        # New links
        for pop in linked:
            r_level = min(level, pop.get_data("pop", "level")) // 10
            logger.info("%s - %s. Linking on layer pop_links%d", self.pop, pop, r_level)
            self.pop.connect_genderless(
                "links", pop, "links", type="pop_link", layer="pop_links%d" % r_level
            )


def update_pop_links(pop_id):
    """
    Handler for delayed call
    """
    LinkedPoP(pop_id).update_links()
