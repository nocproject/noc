# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## One-time job to update PoP links
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link


class UpdatePopLinksJob(IntervalJob):
    name = "inv.update_pop_links"
    model = Object
    interval = 7 * 86400
    randomize = True
    threaded = True
    ignored = False
    group = "update_pop_links"
    concurrency = 1
    initial_submit_interval = 600
    initial_submit_concurrency = 1000

    @classmethod
    def can_submit(self, object):
        return bool(object.get_data("pop", "level"))

    @classmethod
    def initial_submit(cls, scheduler, keys):
        now = datetime.datetime.now()
        isc = cls.initial_submit_concurrency
        pop_models = [m.id for m in ObjectModel.objects.filter(data__pop__level__exists=True)]
        for o in Object.objects.filter(model__in=pop_models).only("id", "model"):
            if o.id not in keys and cls.can_submit(o):
                cls.submit(
                    scheduler=scheduler,
                    key=o.id,
                    interval=cls.interval,
                    failed_interval=cls.interval / 2,
                    randomize=True,
                    ts=now - datetime.timedelta(
                        seconds=random.random() * cls.initial_submit_interval))
                isc -= 1
                if not isc:
                    break

    def get_display_key(self):
        if self.object:
            return self.object.name
        else:
            return self.key

    def get_db_links(self):
        """
        Yield remote pop, level
        """
        for c, remote, _ in self.object.get_genderless_connections("links"):
            yield c, remote, c.data["level"]

    def get_pop_objects(self, root=None):
        """
        Get managed objects inside PoP
        """
        if not root:
            root = self.object
        mos = set()
        for o in root.get_content():
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
        self_objects = set(self.get_pop_objects())
        self_interfaces = set(i.id for i in Interface.objects.filter(managed_object__in=self_objects))
        for l in Link.objects.filter(interfaces__in=self_interfaces):
            ri = (i for i in l.interfaces if i.id not in self_interfaces)
            if ri:
                # Remote link
                ro = set()
                for i in ri:
                    ro.add(i.managed_object.id)
                if len(ro) == 1 and ro:
                    for o in Object.get_managed(ro.pop()):
                        pop = o.get_pop()
                        if pop and pop not in linked:
                            linked.add(pop)
        return linked

    def handler(self, *args, **kwargs):
        level = self.object.get_data("pop", "level")
        linked = self.get_linked_pops()
        for c, pop, l_level in self.get_db_links():
            r_level = min(level, l_level)
            if pop in linked:
                # Already linked
                if r_level != l_level:
                    # Adjust link level
                    self.info("%s - %s. Changing link level to %d" % (
                        self.object, pop, r_level
                    ))
                    c.data["level"] = r_level
                    c.save()
                linked.remove(pop)
            else:
                # Unlink
                self.info("Unlinking %s - %s" % (self.object, pop))
                c.delete()
        # New links
        for pop in linked:
            r_level = min(level, pop.get_data("pop", "level"))
            self.info("%s - %s. Linking with level %d" % (
                self.object, pop, r_level
            ))
            self.object.connect_genderless(
                "links", pop, "links",
                {"level": r_level}, type="pop_link")
        return True
