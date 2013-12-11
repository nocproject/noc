# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.connectiontype application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.connectiontype import ConnectionType
from noc.main.models.collectioncache import CollectionCache


class ConnectionTypeApplication(ExtDocApplication):
    """
    ConnectionType application
    """
    title = "Connection Types"
    menu = "Setup | Connection Types"
    model = ConnectionType
    query_fields = ["name__icontains", "description__icontains"]

    def field_is_builtin(self, o):
        return bool(CollectionCache.objects.filter(uuid=o.uuid))

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_to_json(self, request, id):
        o = self.get_object_or_404(ConnectionType, id=id)
        return o.to_json()

    @view(url="^(?P<id>[0-9a-f]{24})/compatible/$", method=["GET"],
          access="read", api=True)
    def api_compatible(self, request, id):
        def fn(t, gender, reason):
            return {
                "id": str(t.id),
                "name": t.name,
                "gender": gender,
                "description": t.description,
                "reason": reason
            }

        def cp(c1, c2):
            """Inheritance path"""
            chain = c1.get_inheritance_path(c2)
            return " --- ".join("[%s]" % x.name for x in chain)

        o = self.get_object_or_404(ConnectionType, id=id)
        r = []
        if "m" in o.genders:
            ##
            ## Type m
            ##
            rr = []
            if "f" in o.genders:
                rr += [fn(o, "f", "Same type")]
            # Superclassess
            for ct in o.get_superclasses():
                rr += [fn(ct, "f", "Superclass %s" % cp(o, ct))]
            # c_groups
            if o.c_group:
                so = set(o.c_group)
                for ct in o.get_by_c_group():
                    rr += [fn(ct, "f", "Share common groups: %s" % ", ".join(so & set(ct.c_group)))]
            r += [{"gender": "m", "records": rr}]
        if "f" in o.genders:
            ##
            ## Type f
            ##
            rr = []
            if "m" in o.genders:
                rr += [fn(o, "m", "Same type")]
            # Superclassess
            for ct in o.get_subclasses():
                rr += [fn(ct, "m", "Subclass %s" % cp(ct, o))]
            # c_group
            if o.c_group:
                so = set(o.c_group)
                for ct in o.get_by_c_group():
                    rr += [fn(ct, "m", "Share common groups: %s" % ", ".join(so & set(ct.c_group)))]
            r += [{"gender": "f", "records": rr}]
        if "s" in o.genders:
            ##
            ## Type s
            ##
            rr = [fn(o, "s", "Same type")]
            # Superclassess
            for ct in o.get_superclasses():
                rr += [fn(ct, "s", "Superclass %s" % cp(o, ct))]
            # Subclasses
            for ct in o.get_subclasses():
                rr += [fn(ct, "s", "Subclass %s" % cp(ct, o))]
            # c_group
            if o.c_group:
                so = set(o.c_group)
                for ct in o.get_by_c_group():
                    rr += [fn(ct, "s", "Share common groups: %s" % ", ".join(so & set(ct.c_group)))]

            r += [{"gender": "s", "records": rr}]
        return r
