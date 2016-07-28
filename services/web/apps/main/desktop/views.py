# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.desktop application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import datetime
import os
## Django modules
from django.http import HttpResponse
## NOC modules
from noc.settings import config
from noc.lib.app import ExtApplication, ModelApplication, view, PermitLogged
from noc.lib.version import get_version, get_brand
from noc.main.models import Group
from noc.main.models.usersession import UserSession
from noc.main.models.userstate import UserState
from noc.main.models.favorites import Favorites
from noc.support.cp import CPClient
from noc.core.service.client import RPCClient, RPCError
from noc.core.translation import ugettext as _


class DesktopApplication(ExtApplication):
    """
    main.desktop application
    """
    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        #
        # Parse themes
        self.default_theme = config.get("customization", "default_theme")
        self.themes = {}  # id -> {name: , css:}
        for o in config.options("themes"):
            if o.endswith(".name"):
                theme_id = o[:-5]
                nk = "%s.name" % theme_id
                ek = "%s.enabled" % theme_id
                if (config.has_option("themes", nk) and
                    config.has_option("themes", ek) and
                    config.getboolean("themes", ek)):
                    self.themes[theme_id] = {
                        "id": theme_id,
                        "name": config.get("themes", nk).strip(),
                        "css": "/static/pkg/extjs/packages/ext-theme-%s/build/resources/ext-theme-%s-all.css" % (theme_id, theme_id),
                        "js": "/static/pkg/extjs/packages/ext-theme-%s/build/ext-theme-%s.js" % (theme_id, theme_id)
                    }
        # Login restrictions
        self.restrict_to_group = self.get_group(
            config.get("authentication", "restrict_to_group"))
        self.single_session_group = self.get_group(
            config.get("authentication", "single_session_group"))
        self.mutual_exclusive_group = self.get_group(
            config.get("authentication", "mutual_exclusive_group"))
        self.idle_timeout = config.getint("authentication", "idle_timeout")

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
        language = self.site.service.config.language
        if user.is_authenticated:
            try:
                profile = user.get_profile()
                if profile.preferred_language:
                    language = profile.preferred_language
            except:
                pass
        return language

    @view(method=["GET"], url="^$", url_name="desktop", access=True)
    def view_desktop(self, request):
        """
        Render application root template
        """
        cp = CPClient()
        ext_apps = [a for a in self.site.apps
                    if isinstance(self.site.apps[a], ExtApplication) or\
                    isinstance(self.site.apps[a], ModelApplication)]
        apps = [a.split(".") for a in sorted(ext_apps)]
        # Prepare settings
        favicon_url = config.get("customization", "favicon_url")
        if favicon_url.endswith(".png"):
            favicon_mime = "image/png"
        elif favicon_url.endswith(".jpg") or favicon_url.endswith(".jpeg"):
            favicon_mime = "image/jpeg"
        else:
            favicon_mime = None

        setup = {
            "system_uuid": cp.system_uuid,
            "installation_name": config.get("customization",
                                            "installation_name"),
            "logo_url": config.get("customization", "logo_url"),
            "logo_width": config.get("customization", "logo_width"),
            "logo_height": config.get("customization", "logo_height"),
            "brand": get_brand(),
            "branding_color": config.get("customization", "branding_color"),
            "branding_background_color": config.get("customization", "branding_background_color"),
            "favicon_url": favicon_url,
            "favicon_mime": favicon_mime,
            "debug_js": config.getboolean("main", "debug_js"),
            "install_collection": config.getboolean("develop", "install_collection"),
            "enable_gis_base_osm": config.getboolean("gis", "enable_osm"),
            "enable_gis_base_google_sat": config.getboolean("gis", "enable_google_sat"),
            "enable_gis_base_google_roadmap": config.getboolean("gis", "enable_google_roadmap"),
            "trace_extjs_events": config.getboolean("main", "trace_extjs_events"),
            "preview_theme": "midnight"

        }
        return self.render(
            request, "desktop.html",
            language=self.get_language(request),
            apps=apps,
            setup=setup
        )

    ##
    ## Exposed Public API
    ##
    @view(method=["GET"], url="^version/$", access=True, api=True)
    def api_version(self, request):
        """
        Return current NOC version

        :returns: version string
        :rtype: Str
        """
        return get_version()

    @view(method=["GET"], url="^is_logged/$", access=True, api=True)
    def api_is_logged(self, request):
        """
        Check wrether the session is authenticated.

        :returns: True if session authenticated, False otherwise
        :rtype: Bool
        """
        return request.user.is_authenticated()

    @view(method=["POST"], url="^logout/$", access=PermitLogged(), api=True)
    def api_logout(self, request):
        """
        Deauthenticate session

        :returns: Logout status: True or False
        :rtype: Bool
        """
        if request.user.is_authenticated():
            UserSession.unregister(request.session.session_key)
            request.session.flush()
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        return True

    @view(method=["GET"], url="^user_settings/$",
          access=PermitLogged(), api=True)
    def api_user_settings(self, request):
        """
        Get user settings
        """
        user = request.user
        return {
            "username": user.username,
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
        client = RPCClient("login", calling_service="web")
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

    @view(method=["GET"], url=r"^theme/lookup/$",
          access=PermitLogged(), api=True)
    def api_theme_lookup(self, request):
        q = dict(request.GET.items())
        limit = q.get("__limit")
        # page = q.get(self.page_param)
        start = q.get("__start")
        format = q.get("__format")
        query = q.get("__query")
        data = [{"id": t["id"], "label": t["name"]}
                for t in self.themes.values()]
        if query:
            data = [t for t in data if query in t["id"] or query in t["label"]]
        data = sorted(data, key=lambda x: x["label"])
        if start is not None and limit is not None:
            data = data[int(start):int(start) + int(limit)]
        if format == "ext":
            data = {
                "total": len(data),
                "success": True,
                "data": data
            }
        return data

    @view(method=["GET"], url=r"^theme/(?P<theme_id>\S+)/$",
          access=PermitLogged(), api=True)
    def api_theme(self, request, theme_id):
        if theme_id not in self.themes:
            return self.response_not_found()
        theme = self.themes[theme_id]
        return {
            "id": theme_id,
            "name": theme["name"],
            "css": theme["css"]
        }

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
                s = UserState(user_id=uid, key=name, value = value)
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
        cp = CPClient()
        return {
            "version": get_version(),
            "installation": config.get("customization",
                                       "installation_name"),
            "system_id": cp.system_uuid,
            "copyright": "2007-%d, The NOC Project" % datetime.date.today().year
        }
