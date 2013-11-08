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
from noc.inv.models.vendor import Vendor


class AssetReport(Report):
    system_notification = "inv.asset_discovery"

    def __init__(self, job, enabled=True, to_save=False):
        super(AssetReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.om_cache = {}  # part_no -> object model
        self.unknown_part_no = {}  # part_no -> list of variants
        self.pn_description = {}  # part_no -> Description
        self.vendors = {}  # code -> Vendor instance

    def submit(self, jid, part_no, vendor=None,
               revision=None, serial=None,
               description=None, connections=None):
        connections = [] if connections is None else connections
        # Cache description
        if description:
            for p in part_no:
                if p not in self.pn_description:
                    self.pn_description[p] = description
        # Find vendor
        vnd = self.get_vendor(vendor)
        if not vnd:
            self.error("Unknown vendor '%s' for S/N %s (%s)" % (
                vendor, serial, description))
            return
        # Find model
        m = self.get_model(vnd, part_no)
        if not m:
            self.register_unknown_part_no(part_no)
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

    def send(self):
        if self.unknown_part_no:
            platform = self.object.platform
            upn = self.get_unknown_part_no()
            for pns in upn:
                # Find description
                description = "no description"
                for p in pns:
                    if p in self.pn_description:
                        description = self.pn_description[p]
                        break
                # Report error
                self.error("Unknown part number for %s: %s (%s)" % (
                    platform, ", ".join(pns), description))

    def get_model(self, vendor, part_no):
        """
        Get ObjectModel by part part_no,
        Search order:
            * NOC model name
            * asset.part_no* value (Part numbers)
            * asset.order_part_no* value (FRU numbers)
        """
        # Process list of part no
        if type(part_no) == list:
            for p in part_no:
                m = self.get_model(vendor, p)
                if m:
                    return m
            return None
        # Process scalar type
        m = self.om_cache.get(part_no)
        if m:
            return m
        # Check for model name
        if " | " in part_no:
            m = ObjectModel.objects.filter(name=part_no).first()
            if m:
                self.om_cache[part_no] = m
                return m
        vq = Q(vendor=vendor.id)
        # Check for asset.part_no*
        q = vq & (
            Q(data__asset__part_no0=part_no) |
            Q(data__asset__part_no1=part_no) |
            Q(data__asset__part_no2=part_no) |
            Q(data__asset__part_no3=part_no)
        )
        m = ObjectModel.objects.filter(q).first()
        if m:
            self.om_cache[part_no] = m
            return m
        # Check for asset.order_part_no*
        q = vq & (
            Q(data__asset__order_part_no0=part_no) |
            Q(data__asset__order_part_no1=part_no) |
            Q(data__asset__order_part_no2=part_no) |
            Q(data__asset__order_part_no3=part_no)
        )
        m = ObjectModel.objects.filter(q).first()
        if m:
            self.om_cache[part_no] = m
            return m
        # Not found
        self.om_cache[part_no] = None
        return None

    def register_unknown_part_no(self, part_no):
        """
        Register missed part number
        """
        if type(part_no) != list:
            part_no = [part_no]
        for p in part_no:
            if p not in self.unknown_part_no:
                self.unknown_part_no[p] = set()
            for pp in part_no:
                self.unknown_part_no[p].add(pp)

    def get_unknown_part_no(self):
        """
        Get list of missed part number variants
        """
        r = []
        for p in self.unknown_part_no:
            n = sorted(self.unknown_part_no[p])
            if n not in r:
                r += [n]
        return r

    def get_vendor(self, v):
        """
        Get vendor instance or None
        """
        if v is None:
            v = "NONAME"
        v = v.upper()
        if v in self.vendors:
            return self.vendors[v]
        o = Vendor.objects.filter(code=v).first()
        if o:
            self.vendors[v] = o
            return o
        else:
            self.vendors[v] = None
            return None
