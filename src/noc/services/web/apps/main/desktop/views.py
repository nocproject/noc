# ---------------------------------------------------------------------
# main.desktop application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import datetime
import os

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.config import config
from noc.services.web.base.extapplication import ExtApplication, api
from noc.services.web.base.access import PermitLogged
from noc.core.version import version
from noc.aaa.models.group import Group
from noc.main.models.userstate import UserState
from noc.main.models.favorites import Favorites
from noc.main.models.style import Style
from noc.aaa.models.permission import Permission
from noc.support.cp import CPClient
from noc.core.feature import active_features


class DesktopApplication(ExtApplication):
    """
    main.desktop application
    """

    def __init__(self, *args, **kwargs) -> None:
        ExtApplication.__init__(self, *args, **kwargs)
        # Login restrictions
        self.restrict_to_group = self.get_group(config.login.restrict_to_group)
        self.single_session_group = self.get_group(config.login.single_session_group)
        self.mutual_exclusive_group = self.get_group(config.login.mutual_exclusive_group)

    def get_group(self, name):
        """
        Get group by name
        :param name: group name
        :return: Group
        """
        if not name:
            return None
        try:
            return Group.objects.get(name=name)
        except Group.DoesNotExist:
            self.logger.error(f"Group '{name}' is not found")
            return None

    def get_language(self, request: HttpRequest):
        """
        Get language for request
        """
        if not request.user:
            return config.language
        return request.user.preferred_language or config.language

    @api.get("/index.html", url_name="desktop", access=True)
    def view_desktop(self, request: HttpRequest):
        """
        Render application root template
        """
        return self.render(
            request,
            "desktop.html",
            language=self.get_language(request),
            theme=config.web.theme,
            brand=config.brand,
        )

    @api.get("^settings/$", access=True)
    def api_settings(self, request: HttpRequest):
        cp = CPClient()
        if request.user.is_authenticated():
            enable_search = Permission.has_perm(request.user, "main:search:launch")
        else:
            enable_search = False
        language = self.get_language(request)
        return {
            "system_uuid": cp.system_uuid or None,
            "brand": config.brand,
            "features": [f.value for f in active_features()],
            "installation_name": config.installation_name,
            "preview_theme": config.customization.preview_theme,
            "language": language,
            "branding_color": config.customization.branding_color,
            "branding_background_color": config.customization.branding_background_color,
            "enable_search": enable_search,
            "collections": {
                "allow_sharing": config.collections.allow_sharing,
                "allow_overwrite": config.collections.allow_overwrite
                and os.access("collections", os.W_OK),
            },
            "gis": {
                "yandex_supported": config.gis.yandex_supported,
                "base": {
                    "enable_blank": config.gis.enable_blank,
                    "enable_osm": config.gis.enable_osm,
                    "enable_google_sat": config.gis.enable_google_sat,
                    "enable_google_roadmap": config.gis.enable_google_roadmap,
                    "enable_google_hybrid": config.gis.enable_google_hybrid,
                    "enable_google_terrain": config.gis.enable_google_terrain,
                    "enable_tile1": config.gis.enable_tile1,
                    "enable_tile2": config.gis.enable_tile1,
                    "enable_tile3": config.gis.enable_tile1,
                    "enable_yandex_sat": config.gis.enable_yandex_sat,
                    "enable_yandex_hybrid": config.gis.enable_yandex_hybrid,
                    "enable_yandex_roadmap": config.gis.enable_yandex_roadmap,
                },
                "custom": {
                    "tile1": {
                        "name": config.gis.tile1_name,
                        "url": config.gis.tile1_url,
                        "subdomains": config.gis.tile1_subdomains or [],
                    },
                    "tile2": {
                        "name": config.gis.tile2_name,
                        "url": config.gis.tile2_url,
                        "subdomains": config.gis.tile2_subdomains or [],
                    },
                    "tile3": {
                        "name": config.gis.tile3_name,
                        "url": config.gis.tile3_url,
                        "subdomains": config.gis.tile3_subdomains or [],
                    },
                },
                "default_layer": config.gis.default_layer,
            },
            "traceExtJSEvents": False,
            "helpUrl": config.help.base_url,
            "helpBranch": config.help.branch,
            "helpLanguage": config.help.language,
            "timezone": str(config.timezone),
            "enable_remote_system_last_extract_info": config.web.enable_remote_system_last_extract_info,
            "theme": config.web.theme,
            "has_geocoder": bool(config.geocoding.ui_geocoder),
            "color_scheme": Style.get_scheme(),
        }

    @api.get("^version/$", access=True)
    def api_version(self, request: HttpRequest):
        """
        Return current NOC version

        :returns: version string
        """
        return version.version

    @api.get("^is_logged/$", access=True)
    def api_is_logged(self, request: HttpRequest):
        """
        Check wrether the session is authenticated.

        :returns: True if session authenticated, False otherwise
        """
        return request.user.is_authenticated()

    @api.get("^user_settings/$", access=PermitLogged())
    def api_user_settings(self, request: HttpRequest):
        """
        Get user settings
        """
        user = request.user
        return {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "can_change_credentials": True,
            "idle_timeout": config.login.idle_timeout,
            "navigation": {
                "id": "root",
                "iconCls": "fa fa-globe",
                "text": "All",
                "leaf": False,
                "expanded": True,
                "children": self.get_navigation(request),
            },
        }

    def get_navigation(self, request: HttpRequest):
        """
        Return user's navigation menu tree

        :returns:
        """

        def get_children(node, user):
            c = []
            for r in node:
                n = {"id": r["id"], "text": r["title"]}
                if "iconCls" in r:
                    n["iconCls"] = r["iconCls"]
                if "children" in r:
                    cld = get_children(r["children"], user)
                    if not cld:
                        continue
                    n["leaf"] = False
                    n["children"] = cld
                    c.append(n)
                elif r["access"](user):
                    n["leaf"] = True
                    n["launch_info"] = r["app"].get_launch_info(request)
                    c.append(n)
            return c

        # Return empty list for unauthenticated user
        if not request.user.is_authenticated():
            return []
        node = request.GET.get("node", "root")
        # For root nodes - show all modules user has access
        if node == "root":
            root = self.site.menu
        else:
            try:
                root = self.site.menu_index[node]["children"]
            except KeyError:
                return self.response_not_found()
        return get_children(root, request.user)

    @api.get("^launch_info/$", access=PermitLogged())
    def api_launch_info(self, request: HttpRequest):
        """
        Get application launch information
        :param node: Menu node id
        :returns: Dict with: 'class' - application class name
        """
        try:
            menu = self.site.menu_index[request.GET["node"]]
            if "children" in menu:
                raise KeyError
        except KeyError:
            return self.response_not_found()
        return menu["app"].get_launch_info(request)

    @api.get("^state/", access=PermitLogged())
    def api_get_state(self, request: HttpRequest):
        """
        Get user state
        :return:
        """
        uid = request.user.id
        return {r.key: r.value for r in UserState.objects.filter(user_id=uid)}

    @api.get("^state/(?P<name>.+)/$", access=PermitLogged())
    def api_get_state_by_name(self, request: HttpRequest, name):
        """
        Get user state
        :return:
        """
        uid = request.user.id
        return {r.key: r.value for r in UserState.objects.filter(user_id=uid, key=name)}

    @api.delete("^state/(?P<name>.+)/$", access=PermitLogged())
    def api_clear_state(self, request: HttpRequest, name):
        """
        Clear user state
        :return:
        """
        uid = request.user.id
        UserState.objects.filter(user_id=uid, key=name).delete()
        return True

    @api.post("^state/(?P<name>.+)/$", access=PermitLogged())
    def api_set_state(self, request: HttpRequest, name):
        """
        Clear user state
        :return:
        """
        uid = request.user.id
        if isinstance(request.body, bytes):
            value = request.body.decode()
        else:
            value = request.body
        if value:
            # Save
            s = UserState.objects.filter(user_id=uid, key=name).first()
            if s:
                s.value = value
            else:
                s = UserState(user_id=uid, key=name, value=value)
            s.save()
        else:
            # Delete state
            UserState.objects.filter(user_id=uid, key=name).delete()
        return True

    @api.get("^favapps/$", access=PermitLogged())
    def api_favapps(self, request: HttpRequest):
        favapps = [
            f.app
            for f in Favorites.objects.filter(user=request.user.id, favorite_app=True).only("app")
        ]
        return [
            {
                "app": fa,
                "title": self.site.apps[fa].title,
                "launch_info": self.site.apps[fa].get_launch_info(request),
            }
            for fa in favapps
        ]

    @api.get("^about/", access=True)
    def api_about(self, request: HttpRequest):
        current_year = datetime.date.today().year
        data = {
            "brand": config.brand,
            "version": version.version,
            "installation": config.installation_name,
            "copyright": f"2007-{current_year}, {config.brand}",
        }
        if config.features.cpclient:
            cp = CPClient()
            data["system_id"] = cp.system_uuid
        return data
