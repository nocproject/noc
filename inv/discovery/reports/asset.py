## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Asset Discovery Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.queryset import Q
## NOC modules
from base import Report
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object


class AssetReport(Report):
    system_notification = "inv.asset_discovery"

    def __init__(self, job, enabled=True, to_save=False):
        super(AssetReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.om_cache = {}  # part_no -> object model

    def submit(self, jid, part_no, revision=None, serial=None,
               description=None, connections=None):
        connections = [] if connections is None else connections
        m = self.get_model(part_no)
        if not m:
            self.error("Model not found for part_no %s" % part_no)
            return
        # Find existing object or create new
        o = Object.objects.filter(
            model=m.id, data__asset__serial=serial).first()
        if not o:
            # Create new object
            self.info("Creating new object. model='%s', serial='%s'" % (
                m.name, serial))
            o = Object(model=m, data={"asset": {"serial": serial}})
            o.save()
        # Check revision
        if o.get_data("asset", "revision") != revision:
            # Update revision
            self.info("Object revision changed [%s %s] %s -> %s" % (
                m.name, o.id, o.get_data("asset", "revision"), revision
            ))
            o.set_data("asset", "revision", revision)
            o.save()

    def get_model(self, part_no):
        """
        Get ObjectModel by part part_no,
        Search order:
            * NOC model name
            * asset.part_no* value (Part numbers)
            * asset.order_part_no* value (FRU numbers)
        """
        m = self.om_cache.get(part_no)
        if m:
            return m
        # Check for model name
        if " | " in part_no:
            m = ObjectModel.objects.filter(name=part_no).first()
            if m:
                self.om_cache[part_no] = m
                return m
        # Check for asset.part_no*
        q = (Q(data__asset__part_no0=part_no) |
             Q(data__asset__part_no1=part_no) |
             Q(data__asset__part_no2=part_no) |
             Q(data__asset__part_no3=part_no))
        m = ObjectModel.objects.filter(q).first()
        if m:
            self.om_cache[part_no] = m
            return m
        # Check for asset.order_part_no*
        q = (Q(data__asset__order_part_no0=part_no) |
             Q(data__asset__order_part_no1=part_no) |
             Q(data__asset__order_part_no2=part_no) |
             Q(data__asset__order_part_no3=part_no))
        m = ObjectModel.objects.filter(q).first()
        if m:
            self.om_cache[part_no] = m
            return m
        # Not found
        self.om_cache[part_no] = None
        return None
