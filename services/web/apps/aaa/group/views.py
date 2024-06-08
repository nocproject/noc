# ---------------------------------------------------------------------
# Group Group Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import threading

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.services.web.base.site import site
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.aaa.models.group import Group
from noc.aaa.models.permission import Permission
from noc.core.translation import ugettext as _

apps_lock = threading.RLock()


class GroupsApplication(ExtModelApplication):
    """
    Group application
    """

    title = _("Groups")
    menu = [_("Setup"), _("Groups")]
    glyph = "users"
    model = Group
    query_condition = "icontains"
    query_fields = ["name"]
    default_ordering = ["name"]
    custom_m2m_fields = {"permissions": Permission}

    @view(method=["GET"], url=r"^(?P<id>\d+)/?$", access="read", api=True)
    def api_read(self, request, id):
        """
        Returns dict with object's fields and values
        """
        try:
            o = self.queryset(request).get(**{self.pk: int(id)})
        except self.model.DoesNotExist:
            return HttpResponse("", status=self.NOT_FOUND)
        only = request.GET.get(self.only_param)
        if only:
            only = only.split(",")
        return self.response(self.instance_to_dict_get(o, fields=only), status=self.OK)

    def instance_to_dict_get(self, o, fields=None):
        r = super().instance_to_dict(o, fields)
        current_perms = Permission.get_group_permissions(o)
        r["permissions"] = [
            {
                "module": p.module,
                "title": p.title,
                "name": p.name,
                "status": p.name in current_perms,
            }
            for p in site.get_app_permissions_list()
        ]
        return r

    def update_m2m(self, o, name, values):
        if values is None:
            return  # Do not touch
        if name == "permissions":
            Permission.set_group_permissions(group=o, perms=values)
        else:
            super().update_m2m(o, name, values)

    @view(method=["GET"], url=r"^new_permissions/$", access="read", api=True)
    def api_read_permission(self, request):
        """
        Returns dict available permissions
        """
        return self.response(
            {
                "data": {
                    "permissions": [
                        {
                            "module": p.module,
                            "title": p.title,
                            "name": p.name,
                            "status": False,
                        }
                        for p in site.get_app_permissions_list()
                    ]
                }
            },
            status=self.OK,
        )
