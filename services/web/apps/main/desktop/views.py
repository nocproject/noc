# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.desktop application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import datetime
# Django modules
from django.http import HttpResponse
from django.contrib.auth.models import Group
# NOC modules
from noc.config import config
from noc.lib.app.extapplication import ExtApplication, view
from noc.lib.app.modelapplication import ModelApplication
from noc.lib.app.access import PermitLogged
from noc.core.version import version
from noc.main.models.userstate import UserState
from noc.main.models.favorites import Favorites
from noc.main.models.permission import Permission
from noc.support.cp import CPClient
from noc.core.service.client import open_sync_rpc, RPCError
from noc.core.translation import ugettext as _


class DesktopApplication(ExtApplication):
    """
    main.desktop application
    """
    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        # Login restrictions
        self.restrict_to_group = self.get_group(config.login.restrict_to_group)
        self.single_session_group = self.get_group(config.login.single_session_group)
        self.mutual_exclusive_group = self.get_group(config.login.mutual_exclusive_group)
        self.idle_timeout = config.login.idle_timeout

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
            self.error("Group '%s' is not found" % name)
            return None

    def get_language(self, request):
        """
        Get theme for request
        """
        user = request.user
        language = config.language
        if user.is_authenticated:
            try:
                profile = user.get_profile()
                if profile.preferred_language:
                    language = profile.preferred_language
            except Exception:
                pass
        return language

    @view(method=["GET"], url="^$", url_name="desktop", access=True)
    def view_desktop(self, request):
        """
        Render application root template
        """
        cp = CPClient()
        ext_apps = [
            a for a in self.site.apps
            if isinstance(self.site.apps[a],
                          (ExtApplication, ModelApplication))
        ]
        apps = [a.split(".") for a in sorted(ext_apps)]
        # Prepare settings
        favicon_url = config.customization.favicon_url
        if favicon_url.endswith(".png"):
            favicon_mime = "image/png"
        elif favicon_url.endswith(".jpg") or favicon_url.endswith(".jpeg"):
            favicon_mime = "image/jpeg"
        else:
            favicon_mime = None
        if request.user.is_authenticated():
            enable_search = Permission.has_perm(request.user, "main:search:launch")
        else:
            enable_search = False
        setup = {
            "system_uuid": cp.system_uuid,
            "installation_name": config.installation_name,
            "logo_url": config.customization.logo_url,
            "logo_width": config.customization.logo_width,
            "logo_height": config.customization.logo_height,
            "brand": version.brand,
            "branding_color": config.customization.branding_color,
            "branding_background_color": config.customization.branding_background_color,
            "favicon_url": favicon_url,
            "favicon_mime": favicon_mime,
            "debug_js": False,
            "install_collection": config.web.install_collection,
            "enable_gis_base_osm": config.gis.enable_osm,
            "enable_gis_base_google_sat": config.gis.enable_google_sat,
            "enable_gis_base_google_roadmap": config.gis.enable_google_roadmap,
            "trace_extjs_events": False,
            "preview_theme": config.customization.preview_theme,
            "enable_search": enable_search
        }
        return self.render(
            request, "desktop.html",
            language=self.get_language(request),
            apps=apps,
            setup=setup
        )

    #
    # Exposed Public API
    #
    @view(method=["GET"], url="^version/$", access=True, api=True)
    def api_version(self, request):
        """
        Return current NOC version

        :returns: version string
        :rtype: Str
        """
        return version.version

    @view(method=["GET"], url="^is_logged/$", access=True, api=True)
    def api_is_logged(self, request):
        """
        Check wrether the session is authenticated.

        :returns: True if session authenticated, False otherwise
        :rtype: Bool
        """
        return request.user.is_authenticated()

    @view(method=["GET"], url="^user_settings/$",
          access=PermitLogged(), api=True)
    def api_user_settings(self, request):
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
            "idle_timeout": self.idle_timeout,
            "navigation": {
                "id": "root",
                "iconCls": "fa fa-globe",
                "text": "All",
                "leaf": False,
                "expanded": True,
                "children": self.get_navigation(request)
            }
        }

    def get_navigation(self, request):
        """
        Return user's navigation menu tree

        :param node:
        :returns:
        """
        def get_children(node, user):
            c = []
            for r in node:
                n = {
                    "id": r["id"],
                    "text": r["title"]
                }
                if "iconCls" in r:
                    n["iconCls"] = r["iconCls"]
                if "children" in r:
                    cld = get_children(r["children"], user)
                    if not cld:
                        continue
                    n["leaf"] = False
                    n["children"] = cld
                    c += [n]
                elif r["access"](user):
                    n["leaf"] = True
                    n["launch_info"] = r["app"].get_launch_info(request)
                    c += [n]
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

    @view(method=["GET"], url="^launch_info/$", access=PermitLogged(),
          api=True)
    def api_launch_info(self, request):
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

    @view(method=["POST"], url="^change_credentials/$",
          access=PermitLogged(), api=True)
    def api_change_credentials(self, request):
        """
        Change user's credentials if allowed by current backend
        """
        credentials = dict((str(k), v) for k, v in request.POST.items())
        credentials["user"] = request.user.username
        client = open_sync_rpc("login", calling_service="web")
        try:
            r = client.change_credentials(credentials)
        except RPCError as e:
            return self.render_json({
                "status": False,
                "error": str(e)
            })
        if r:
            return self.render_json({
                "status": True
            })
        else:
            return self.render_json({
                "status": False,
                "error": _("Failed to change credentials")
            })

    @view(method=["POST"], url="^dlproxy/$", access=True, api=True)
    def api_dlproxy(self, request):
        """
        Get POST request and return as downloadable file
        """
        ct = request.POST.get("content_type", "text/plain")
        fn = request.POST.get("filename", "file")
        data = request.POST.get("data", "")
        r = HttpResponse(data, content_type=ct)
        r["Content-Disposition"] = "attachment; filename=%s" % fn
        return r

    @view(method=["GET"], url="^state/", access=PermitLogged(), api=True)
    def api_get_state(self, request):
        """
        Get user state
        :param request:
        :return:
        """
        uid = request.user.id
        r = dict((r.key, r.value)
                 for r in UserState.objects.filter(user_id=uid))
        return r

    @view(method=["DELETE"], url="^state/(?P<name>.+)/$",
          access=PermitLogged(), api=True)
    def api_clear_state(self, request, name):
        """
        Clear user state
        :param request:
        :param name:
        :return:
        """
        uid = request.user.id
        UserState.objects.filter(user_id=uid, key=name).delete()
        return True

    @view(method=["POST"], url="^state/(?P<name>.+)/$",
          access=PermitLogged(), api=True)
    def api_set_state(self, request, name):
        """
        Clear user state
        :param request:
        :param name:
        :return:
        """
        uid = request.user.id
        value = request.raw_post_data
        if not value:
            # Delete state
            UserState.objects.filter(user_id=uid, key=name).delete()
        else:
            # Save
            s = UserState.objects.filter(user_id=uid, key=name).first()
            if s:
                s.value = value
            else:
                s = UserState(user_id=uid, key=name, value=value)
            s.save()
        return True

    @view(url="^favapps/$", method=["GET"],
          access=PermitLogged(), api=True)
    def api_favapps(self, request):
        favapps = [f.app for f in
                   Favorites.objects.filter(
                       user=request.user.id,
                       favorite_app=True).only("app")]
        return [
            {
                "app": fa,
                "title": self.site.apps[fa].title,
                "launch_info": self.site.apps[fa].get_launch_info(request)
            } for fa in favapps
        ]

    @view(url="^about/", method=["GET"], access=True, api=True)
    def api_about(self, request):
        if config.features.cpclient:
            cp = CPClient()
            return {
                "logo_url": config.customization.logo_url,
                "brand": config.brand,
                "version": version.version,
                "installation": config.installation_name,
                "system_id": cp.system_uuid,
                "copyright": "2007-%d, The NOC Project" % datetime.date.today().year
            }
        else:
            return {
                "logo_url": config.customization.logo_url,
                "brand": config.brand,
                "version": version.version,
                "installation": config.installation_name,
                "copyright": "2007-%d, %s" % (datetime.date.today().year, config.brand)
            }
