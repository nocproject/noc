# ---------------------------------------------------------------------
# Group Group Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import threading

# Third-party modules
from django.http import HttpResponse
from django.conf import settings

# NOC modules
from noc.services.web.base.site import site
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.aaa.models.group import Group
from noc.aaa.models.permission import Permission
from noc.core.cache.decorator import cachedmethod
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

    @classmethod
    @cachedmethod(key="apps_permissions_list", lock=lambda _: apps_lock)
    def apps_permissions_list(cls):
        r = []
        apps = list(site.apps)
        perms = Permission.objects.values_list("name", flat=True)
        for module in [m for m in settings.INSTALLED_APPS if m.startswith("noc.")]:
            mod = module[4:]
            m = __import__("noc.services.web.apps.%s" % mod, {}, {}, "MODULE_NAME")
            for app in [app for app in apps if app.startswith(mod + ".")]:
                app_perms = sorted([p for p in perms if p.startswith(app.replace(".", ":") + ":")])
                a = site.apps[app]
                if app_perms:
                    for p in app_perms:
                        r += [
                            {
                                "module": m.MODULE_NAME,
                                "title": str(a.title),
                                "name": p,
                                "status": False,
                            }
                        ]
        return r

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
        r["permissions"] = self.apps_permissions_list()
        current_perms = Permission.get_group_permissions(o)
        if current_perms:
            for p in r["permissions"]:
                if p["name"] in current_perms:
                    p["status"] = True
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
            {"data": {"permissions": self.apps_permissions_list()}}, status=self.OK
        )
