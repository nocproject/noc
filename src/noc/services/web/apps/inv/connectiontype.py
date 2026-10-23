# ---------------------------------------------------------------------
# inv.connectiontype application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.inv.models.modelinterface import ModelInterface
from noc.inv.models.connectiontype import ConnectionType
from noc.main.models.doccategory import DocCategory
from noc.core.translation import ugettext as _


class ConnectionTypeApplication(ExtDocApplication):
    """
    ConnectionType application
    """

    title = _("Connection Types")
    menu = [_("Setup"), _("Connection Types")]
    model = ConnectionType
    parent_model = DocCategory
    parent_field = "parent"
    query_fields = ["name__icontains", "description__icontains"]

    def clean(self, data):
        if "data" in data:
            data["data"] = ModelInterface.clean_data(data["data"])
        return super().clean(data)

    @api.get("^(?P<id>[0-9a-f]{24})/compatible/$", access="read")
    def api_compatible(self, request: HttpRequest, id):
        def fn(t, gender, reason):
            return {
                "id": str(t.id),
                "name": t.name,
                "gender": gender,
                "description": t.description,
                "reason": reason,
            }

        def cp(c1, c2):
            """Inheritance path"""
            chain = c1.get_inheritance_path(c2)
            return " --- ".join(f"[{x.name}]" for x in chain)

        o = self.get_object_or_404(ConnectionType, id=id)
        r = []
        if "m" in o.genders:
            # Type m
            rr = []
            if "f" in o.genders:
                rr.append(fn(o, "f", "Same type"))
            # Superclassess
            for ct in o.get_superclasses():
                rr.append(fn(ct, "f", f"Superclass {cp(o, ct)}"))
            # c_groups
            if o.c_group:
                so = set(o.c_group)
                for ct in o.get_by_c_group():
                    rr.append(
                        fn(
                            ct,
                            "f",
                            f"Share common groups: {', '.join(so & set(ct.c_group))}",
                        )
                    )
            r.append({"gender": "m", "records": rr})
        if "f" in o.genders:
            # Type f
            rr = []
            if "m" in o.genders:
                rr.append(fn(o, "m", "Same type"))
            # Superclassess
            for ct in o.get_subclasses():
                rr.append(fn(ct, "m", f"Subclass {cp(ct, o)}"))
            # c_group
            if o.c_group:
                so = set(o.c_group)
                for ct in o.get_by_c_group():
                    rr.append(
                        fn(
                            ct,
                            "m",
                            f"Share common groups: {', '.join(so & set(ct.c_group))}",
                        )
                    )
            r.append({"gender": "f", "records": rr})
        if "s" in o.genders:
            # Type s
            rr = [fn(o, "s", "Same type")]
            # Superclassess
            for ct in o.get_superclasses():
                rr.append(fn(ct, "s", f"Superclass {cp(o, ct)}"))
            # Subclasses
            for ct in o.get_subclasses():
                rr.append(fn(ct, "s", f"Subclass {cp(ct, o)}"))
            # c_group
            if o.c_group:
                so = set(o.c_group)
                for ct in o.get_by_c_group():
                    rr.append(
                        fn(
                            ct,
                            "s",
                            f"Share common groups: {', '.join(so & set(ct.c_group))}",
                        )
                    )

            r.append({"gender": "s", "records": rr})
        return r
