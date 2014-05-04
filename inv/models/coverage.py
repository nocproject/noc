## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Coverage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField)


class Coverage(Document):
    meta = {
        "collection": "noc.coverage",
        "allow_inheritance": False,
    }
    # Subscriber name
    name = StringField(unique=True)
    # Arbitrary description
    description = StringField(required=False)

    def __unicode__(self):
        return self.name

    def get_interfaces(self, technology=None):
        """
        Returns list of interfaces providing coverage.
        Coverage can be limited to particular technology
        """
        from interface import Interface
        q = Interface.objects.filter(coverage=self.id)
        if technology:
            q = q.filter(technologies=technology)
        return list(q)

    @classmethod
    def coverage_for_object(cls, object):
        """
        Returns list of coverages for inventory object
        """
        from coveredobject import CoveredObject
        if hasattr(object, "id"):
            object = object.id
        r = []
        for co in CoveredObject.objects.filter(object=object):
            if co.preference:
                r += [(co.coverage, co.preference)]
        if r:
            return [x[0] for x in sorted(r, key=lambda y: -y[1]) if x[1]]
        elif object.container:
            return cls.coverage_for_object(object.container)
        else:
            return []

    @classmethod
    def coverage_for_building(cls, building, entrance=None):
        """
        Returns list of coverages for building
        """
        from coveredbuilding import CoveredBuilding
        if hasattr(building, "id"):
            building = building.id
        # Get building coverage
        c = {}
        for cb in CoveredBuilding.objects.filter(
                building=building, entrace__exists=False):
            c[cb.coverage] = cb.preference
        # Apply entrance coverage
        if entrance:
            for cb in CoveredBuilding.objects.filter(
                    building=building, entrance=entrance):
                c[cb.coverage] = cb.preference
        return [x[0] for x in sorted(c.items(), key=lambda y: -y[1]) if x[1]]
