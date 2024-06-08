# ---------------------------------------------------------------------
# inv.container application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object


class ObjectContainerApplication(ExtApplication):
    """
    Container application lookup
    """

    menu = None
    query_fields = ["name__icontains", "description__icontains"]

    def queryset(self, request, query=None):
        # if not request.user.is_superuser:
        # qs = qs.filter(adm_domains__in=UserAccess.get_domains(request.user))
        models = list(
            ObjectModel.objects.filter(
                data__match={"interface": "container", "attr": "container", "value": True}
            )
        )
        qs = Object.objects.filter(model__in=models)
        return qs

    def cleaned_query(self, q):
        q = q.copy()
        for p in self.ignored_params:
            if p in q:
                del q[p]
        for p in (
            self.limit_param,
            self.page_param,
            self.start_param,
            self.format_param,
            self.sort_param,
            self.query_param,
            self.only_param,
        ):
            if p in q:
                del q[p]
        if "id" not in q:
            q["container"] = q.pop("parent", None) or None
        return q

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": (o.name), "has_children": o.has_children}

    @view(method=["GET"], url=r"^lookup/$", access="lookup", api=True)
    def api_lookup(self, request):
        return self.list_data(request, self.instance_to_lookup)

    @view("^(?P<oid>[0-9a-f]{24})/get_path/$", access="read", api=True)
    def api_get_path(self, request, oid):
        o = self.get_object_or_404(Object, id=oid)
        path = [Object.get_by_id(ns) for ns in o.get_path()]
        return {
            "data": [
                {"level": level + 1, "id": str(p.id), "label": p.name}
                for level, p in enumerate(path)
            ]
        }
