## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InterfaceStatus model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, IntField)


class InterfaceStatus(Document):
    meta = {
        "collection": "noc.interfacestatus",
        "allow_inheritance": False,
        "indexes": ["object", ("object", "name")]
    }

    # Managed object reference
    object = IntField(required=True)
    # Interface name
    name = StringField()
    #
    admin_status = BooleanField()
    #
    oper_status = BooleanField()
    #
    err_disable = BooleanField()
    # Broken interface
    broken = BooleanField(default=False)

    def __unicode__(self):
        return u"%s:%s" % (self.object, self.name)

    @classmethod
    def get_status(cls, mo, name):
        return InterfaceStatus.objects.filter(
            object=mo.id, name=name).first()

    @classmethod
    def set_status(cls, mo, name,
                   admin_status=None, oper_status=None,
                   err_disable=None, broken=None):
        i_name = mo.profile.convert_interface_name(name)
        s = cls.objects.filter(object=mo.id, name=i_name).first()
        if not s:
            s = InterfaceStatus(object=mo.id, name=i_name)
        if admin_status is not None:
            s.admin_status = admin_status
        if oper_status is not None:
            s.oper_status = oper_status
            if oper_status:
                s.admin_status = True
                s.broken = False
                s.err_disable = False
        if err_disable is not None:
            s.err_disable = err_disable
            if err_disable:
                s.oper_status = False
        if broken is not None:
            s.broken = broken
        s.save()

