# ----------------------------------------------------------------------
#  main.home application
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2025 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any
import importlib.resources

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
from noc.inv.models.techdomain import TechDomain
from noc.inv.models.channel import Channel
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.profile import Profile


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
            self.get_welcome(user),
            self.get_community(user),
            self.get_favorites(user),
            self.get_channels(user),
            self.get_inventory_summary(user),
            self.get_mo_summary(user),
            self.get_alarms(user),
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
        pkg = "noc.services.web.apps.main.home.templates"
        with importlib.resources.files(pkg).joinpath(name).open("r") as fp:
            tpl = Template(fp.read())
            return tpl.render()

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
            "title": _("Community"),
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
        mo_count_q = ManagedObject.objects
        if not user.is_superuser:
            mo_count_q = mo_count_q.filter(UserAccess.Q(user))
        p_sae = Profile.get_by_name("NOC.SAE")
        if p_sae:
            # Still in system
            mo_count_q = mo_count_q.exclude(profile=p_sae.id)
        total_mo = mo_count_q.count()
        return {
            "type": "summary",
            "title": _("Managed Object Summary"),
            "height": "small",
            "items": [
                {
                    "text": _("Managed Objects"),
                    "value": total_mo,
                },
            ],
        }

    def get_alarms(self, user: User) -> Optional[Dict[str, Any]]:
        """
        Generate managed object summary widget.
        """
        if not Permission.has_perm(user, "fm:alarm:launch"):
            return None  # No access to alarms
        if user.is_superuser:
            total_alarms = ActiveAlarm.objects.filter().count()
        else:
            total_alarms = ActiveAlarm.objects.filter(
                adm_path__in=UserAccess.get_domains(user)
            ).count()
        return {
            "type": "summary",
            "title": _("Total Alarms"),
            "height": "small",
            "items": [
                {
                    "text": _("Alarms"),
                    "value": total_alarms,
                },
            ],
        }

    def get_channels(self, user: User) -> Optional[Dict[str, Any]]:
        if not Permission.has_perm(user, "inv:channel:launch"):
            return None  # No access to channels
        summary = {
            doc["_id"]: doc["count"]
            for doc in Channel._get_collection().aggregate(
                [{"$group": {"_id": "$tech_domain", "count": {"$sum": 1}}}]
            )
        }
        td_map = {
            doc["_id"]: doc["name"]
            for doc in TechDomain._get_collection().find(
                {"_id": {"$in": list(summary)}}, {"_id": 1, "name": 1}
            )
        }
        items = [
            {"text": td_map[k], "value": v}
            for k, v in sorted(summary.items(), key=lambda x: x[1], reverse=True)
        ]
        return {"type": "summary", "title": _("Channels"), "height": "medium", "items": items}
