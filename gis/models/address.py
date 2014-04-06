# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Address object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, DictField
## NOC modules
from street import Street
from building import Building
from noc.lib.nosql import PlainReferenceField


class Address(Document):
    meta = {
        "collection": "noc.addresses",
        "allow_inheritance": False
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

    data = DictField()

    def display_ru(self):
        """
        Russian-style display
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
        if self.street:
            if self.street.short_name:
                if self.street.short_name in RU_SHORT_AFTER:
                    st = "%s %s" % (self.street.name, self.street.short_name)
                else:
                    st = "%s %s" % (self.street.short_name, self.street.name)
            else:
                st = self.street.name
            return "%s %s" % (st, " ".join(a))
        else:
            return " ".join(a)

##
RU_SHORT_AFTER = set([u"б-р", u"проезд", u"пер", u"ш"])
