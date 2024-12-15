# ---------------------------------------------------------------------
# User Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.services.web.base.site import site
from noc.services.web.base.extmodelapplication import ExtModelApplication, view
from noc.aaa.models.permission import Permission
from noc.sa.interfaces.base import StringParameter
from noc.core.translation import ugettext as _
from noc.aaa.models.user import User


class UsernameParameter(StringParameter):
    user_validate = re.compile(r"^[\w.@+-]+$")

    def clean(self, value):
        r = super().clean(value)
        match = self.user_validate.match(value)
        if not match:
            raise self.raise_error(
                value, msg="This value must contain only letters, digits and @/./+/-/_."
            )
        return r


class UserApplication(ExtModelApplication):
    model = User

    glyph = "user"
    menu = [_("Setup"), _("Users")]
    icon = "icon_user"
    title = _("Users")
    app_alias = "auth"
    query_condition = "icontains"
    query_fields = ["username", "last_name", "email"]
    default_ordering = ["username"]
    clean_fields = {
        "username": UsernameParameter(),
        "first_name": StringParameter(default=""),
        "last_name": StringParameter(default=""),
        "email": StringParameter(default=""),
    }
    ignored_fields = {"id", "bi_id", "password"}
    custom_m2m_fields = {"permissions": Permission}

    @view(method=["POST"], url=r"^$", access="create", api=True)
    def api_create(self, request):
        response = super().api_create(request)
        if response.status_code == self.CREATED:
            user_id = self.deserialize(response.content).get("id")
            user = self.get_object_or_404(self.model, pk=user_id)
            attrs = (
                self.deserialize(request.body)
                if self.site.is_json(request.META.get("CONTENT_TYPE"))
                else self.deserialize_form(request)
            )
            user.set_password(attrs["password"], save=False)
            user.save()
        return response

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
        del r["password"]
        current_perms = Permission.get_user_permissions(o)
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

    def clean_list_data(self, data):
        """
        Finally process list_data result. Override to enrich with
        additional fields
        :param data:
        :return:
        """
        r = super().apply_bulk_fields(data=data)
        for x in r:
            if "password" in x:
                del x["password"]
        return r

    def update_m2m(self, o, name, values):
        if values is None:
            return  # Do not touch
        if name == "permissions":
            Permission.set_user_permissions(user=o, perms=values)
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

    @view(
        url=r"^(\d+)/password/$",
        method=["POST"],
        access="change",
        validate={"password": StringParameter(required=True)},
    )
    def view_change_password(self, request, object_id, password):
        """
        Change user's password
        :param request:
        :param object_id:
        :param password:
        :return:
        """
        if not request.user.is_superuser:
            return self.response_forbidden("Permission denied")
        user = self.get_object_or_404(self.model, pk=object_id)
        try:
            user.set_password(password)
        except ValueError as e:
            return self.response({"result": str(e.args[0]), "status": False}, self.BAD_REQUEST)
        return self.response({"result": "Password changed", "status": True}, self.OK)

    def can_delete(self, user, obj=None):
        """Disable 'Delete' button"""
        return False
