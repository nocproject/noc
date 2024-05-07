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


class HomeAppplication(ExtApplication):
    """
    main.home application
    """

    title = _("Home")
    _welcome_text: Optional[str] = None

    @view("^dashboard/", access=True, api=True)
    def api_welcome(self, request):
        user = request.user
        widgets = [
            self.get_favorites(user),
            self.get_inventory_summary(user),
            self.get_welcome(user),
        ]
        return {"widgets": [x for x in widgets if x]}

    def get_favorites(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate favorites widget.
        """
        return None

    def get_welcome(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate welcome text.
        """
        if self._welcome_text is None:
            for p in config.get_customized_paths(
                os.path.join(
                    "services", "web", "apps", "main", "home", "templates", "Welcome.html.j2"
                ),
                prefer_custom=True,
            ):
                if not os.path.exists(p):
                    continue
                with open(p) as f:
                    tpl = Template(f.read())
                self._welcome_text = tpl.render()
        return {
            "type": "text",
            "title": _("Welcome to ") + config.brand,
            "data": {"text": self._welcome_text or ""},
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
        pop_models = ObjectModel.objects.filter(data__match={"interface": "pop", "attr": "level", "value__gte": 0}).values_list("id")
        total_pops = Object.objects.filter(model__in=pop_models).count()
        # Racks
        rack_models = ObjectModel.objects.filter(data__match={"interface": "rack", "attr": "units", "value__gte": 0}).values_list("id")
        total_racks = Object.objects.filter(model__in=rack_models).count()
        # Chassis
        # Transceivers
        return {
            "type": "summary",
            "title": _("Inventory summary"),
            "items": [
                {
                    "text": _("Total objects"),
                    "value": total_objects,
                },
                {
                    "text": _("Points of presence"),
                    "value": total_pops
                },
                {
                    "text": _("Racks"),
                    "value": total_racks
                }
            ],
        }
