# ----------------------------------------------------------------------
#  main.home application
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2024 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any
import os

# Third-party modules
from jinja2 import Template

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _
from noc.aaa.models.user import User
from noc.config import config
from noc.aaa.models.permission import Permission
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject


class HomeAppplication(ExtApplication):
    """
    main.home application
    """

    title = _("Home")
    _welcome_text: Optional[str] = None
    _community_text: Optional[str] = None

    @view("^dashboard/", access=True, api=True)
    def api_welcome(self, request):
        user = request.user
        widgets = [
            self.get_favorites(user),
            self.get_inventory_summary(user),
            self.get_mo_summary(user),
            self.get_welcome(user),
            self.get_community(user),
        ]
        return {"widgets": [x for x in widgets if x]}

    def get_favorites(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate favorites widget.
        """
        return None

    def _render_template(self, name: str) -> str:
        """
        Render named template.

        Args:
            name: File name.

        Returns:
            Rendered template as text.
        """
        for p in config.get_customized_paths(
            os.path.join("services", "web", "apps", "main", "home", "templates", name),
            prefer_custom=True,
        ):
            if not os.path.exists(p):
                continue
            with open(p) as f:
                tpl = Template(f.read())
            return tpl.render()
        return ""

    def get_welcome(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate welcome text.
        """
        if self._welcome_text is None:
            self._welcome_text = self._render_template("Welcome.html.j2")
        return {
            "type": "text",
            "title": _("Welcome to ") + config.brand,
            "data": {"text": self._welcome_text or ""},
        }

    def get_community(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate community links
        """
        if self._community_text is None:
            self._comminity_text = self._render_template("Community.html.j2")
        return {
            "type": "text",
            "title": _("Commiunity"),
            "data": {"text": self._comminity_text or ""},
        }

    def get_inventory_summary(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate inventory summary widget.
        """
        if not Permission.has_perm(user, "inv:inv:launch"):
            return None  # No access to inventory
        # Total amount of objects
        total_objects = Object.objects.count()
        # Point of presences
        pop_models = ObjectModel.objects.filter(
            data__match={"interface": "pop", "attr": "level", "value__gte": 0}
        ).values_list("id")
        total_pops = Object.objects.filter(model__in=pop_models).count()
        # Racks
        rack_models = ObjectModel.objects.filter(
            data__match={"interface": "rack", "attr": "units", "value__gte": 0}
        ).values_list("id")
        total_racks = Object.objects.filter(model__in=rack_models).count()
        # Chassis
        chassis_models = ObjectModel.objects.filter(cr_context="CHASSIS").values_list("id")
        total_chassis = Object.objects.filter(model__in=chassis_models).count()
        # Transceivers
        return {
            "type": "summary",
            "title": _("Inventory summary"),
            "items": [
                {
                    "text": _("Total objects"),
                    "value": total_objects,
                },
                {"text": _("Points of presence"), "value": total_pops},
                {"text": _("Racks"), "value": total_racks},
                {"text": _("Chassis"), "value": total_chassis},
            ],
        }

    def get_mo_summary(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate managed object summary widget.
        """
        if not Permission.has_perm(user, "sa:managedobject:launch"):
            return None  # No access to MO
        mo_count_q = ManagedObject.objects.all()
        if not user.is_superuser:
            mo_count_q = mo_count_q.filter(UserAccess.Q(user))
        total_mo = mo_count_q.count()
        return {
            "type": "summary",
            "title": _("Managed Object Summary"),
            "items": [
                {
                    "text": _("Managed Objects"),
                    "value": total_mo,
                },
            ],
        }
