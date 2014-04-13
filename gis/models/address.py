# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Address object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, DictField, BooleanField
from mongoengine.signals import post_save
## NOC modules
from street import Street
from building import Building
from noc.lib.nosql import PlainReferenceField


class Address(Document):
    meta = {
        "collection": "noc.addresses",
        "allow_inheritance": False,
        "indexes": ["building", "street"]
    }
    #
    building = PlainReferenceField(Building)
    # Address part
    street = PlainReferenceField(Street)
    # Number
    num = IntField()
    num2 = IntField()  # Corner number
    num_letter = StringField()
    # Building
    build = IntField()
    build_letter = StringField()
    # Structure
    struct = IntField()
    struct2 = IntField()
    struct_letter = StringField()
    # Estate
    estate = IntField()
    estate2 = IntField()
    estate_letter = StringField()

    data = DictField()

    is_primary = BooleanField(default=True)

    @classmethod
    def update_primary(cls, sender, document, **kwargs):
        """
        Reset other primary addresses from building
        """
        def q(x):
            return x if x else ""

        def nq(x):
            if not x:
                x = 0
            return "%06d" % x

        if document.is_primary:
            # Reset other primary addresses
            Address._get_collection().update({
                "building": document.building.id,
                "$ne": {
                    "id": document.id
                }
            }, {
                "$set": {
                    "is_primary": False
                }
            })
            # Fill sort order
            so = "|".join((str(x) if x else "") for x in [
                document.street.name,
                q(document.street.short_name),
                nq(document.num),
                q(document.num_letter),
                nq(document.num2),
                nq(document.build),
                q(document.build_letter),
                nq(document.struct),
                q(document.struct_letter),
                nq(document.struct2),
                nq(document.estate),
                q(document.estate_letter),
                nq(document.estate2)
            ])
            Building._get_collection().update({
                "_id": document.building.id
            }, {
                "$set": {
                    "sort_order": so
                }
            })


    def display_ru(self, levels=0, to_level=None, sep=", "):
        """
        Russian-style short display
        :param levels: Number of division levels above street to show
        """
        # House number
        a = []
        if self.num:
            if self.num2:
                n = "%d/%d" % (self.num, self.num2)
            else:
                n = str(self.num)
            if self.num_letter:
                n += self.num_letter
            a += ["д. %s" % n]
        if self.estate:
            if self.estate2:
                n = "%d/%d" % (self.estate, self.estate2)
            else:
                n = str(self.estate)
            if self.estate_letter:
                n += self.estate_letter
            a += ["вл. %s" % n]
        if self.build:
            n = str(self.build)
            if self.build_letter:
                n += self.build_letter
            a += ["к. %s" % n]
        if self.struct:
            if self.struct2:
                n = "%d/%d" % (self.struct, self.struct2)
            else:
                n = str(self.struct)
            if self.struct_letter:
                n += self.struct_letter
            a += ["стр. %s" % n]
        # Add street
        n = []
        if self.street:
            if self.street.short_name:
                if self.street.short_name in RU_SHORT_AFTER:
                    st = "%s %s" % (self.street.name, self.street.short_name)
                else:
                    st = "%s %s" % (self.street.short_name, self.street.name)
            else:
                st = self.street.name
            n += ["%s %s" % (st, " ".join(a))]
        else:
            n += [" ".join(a)]
        if levels or to_level is not None:
            if to_level is not None:
                levels = 10
            p = self.building.adm_division
            while p and levels:
                if to_level is not None and p.level == to_level:
                    break
                if p.short_name:
                    n = ["%s %s" % (p.short_name, p.name)] + n
                else:
                    n = [p.name] + n
                p = p.parent
                levels -= 1
        return sep.join(n)

    # @todo: cmp_addr

##
RU_SHORT_AFTER = set([u"б-р", u"проезд", u"пер", u"ш"])

## Signals
post_save.connect(Address.update_primary, sender=Address)
