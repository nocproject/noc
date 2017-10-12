# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Object segmentation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import threading
# Third-party modules
import cachetools
import jinja2
# NOC modules
from noc.inv.models.networksegment import NetworkSegment
from noc.services.discovery.jobs.base import DiscoveryCheck

tpl_lock = threading.Lock()


class SegmentationCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "segmentation"
    required_artefacts = ["seen_objects"]
    tpl_cache = cachetools.TTLCache(100, 300)

    def is_enabled(self):
        return self.object.enable_autosegmentation

    def handler(self):
        self.seg_cache = {}
        seen_objects = self.get_artefact("seen_objects")
        s_objects = {}
        for iface in seen_objects:
            if iface.get_profile().enable_segmentation:
                s_objects[iface] = seen_objects[iface]
        return self.segmentation(s_objects)

    def segmentation(self, if_map):
        """
        Perform segmentation of seen objects
        :param if_map:
        :param target_segment:
        :return:
        """
        sp = self.object.get_autosegmentation_policy()
        max_level = self.object.object_profile.autosegmentation_level_limit
        for iface in if_map:
            # Move all related objects to target segment
            for mo in if_map[iface]:
                # Detect target segment
                if sp == "o":
                    new_segment = self.object.segment
                elif sp == "c":
                    new_segment = self.get_segment(
                        object=self.object,
                        interface=iface,
                        remote_object=mo
                    )
                else:
                    continue
                if not new_segment:
                    self.logger.debug(
                        "[%s|%s] No target segment. Skipping",
                        mo.name,
                        mo.address
                    )
                    continue
                if new_segment != mo.segment:
                    if max_level and mo.object_profile.level > max_level:
                        self.logger.info(
                            "[%s|%s] Object level too high (%s > %s). Skipping",
                            mo.name, mo.address,
                            mo.object_profile.level, max_level
                        )
                        continue
                    if mo.allow_autosegmentation:
                        self.logger.info(
                            "[%s|%s] Changing segment: %s -> %s",
                            mo.name,
                            mo.address,
                            mo.segment.name,
                            new_segment.name
                        )
                        mo.segment = new_segment
                        mo.save()
                    else:
                        self.logger.info(
                            "[%s|%s] Autosegmentation is disabled, skipping",
                            mo.name,
                            mo.address
                        )

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("tpl_cache"),
                             lock=lambda _: tpl_lock)
    def get_template(self, tpl):
        return jinja2.Template(tpl)

    def get_segment(self, **kwargs):
        tpl = self.get_template(self.object_profile.autosegmentation_segment_name)
        name = tpl.render(**kwargs)
        return self.ensure_segment(name)

    @cachetools.cachedmethod(operator.attrgetter("seg_cache"))
    def ensure_segment(self, name):
        ns = NetworkSegment.objects.filter(
            parent=self.object.segment.id,
            name=name
        ).first()
        if not ns:
            root = self.object.segment
            if root.profile:
                profile = root.profile.autocreated_profile or root.profile
            else:
                profile = None

            ns = NetworkSegment(
                parent=self.object.segment,
                name=name,
                profile=profile,
                description="Autocreated by segmentation"
            )
            ns.save()
        return ns
