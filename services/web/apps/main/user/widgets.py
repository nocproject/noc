# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# User Access Widget
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
from noc.lib.app.site import site
from noc.main.models.permission import Permission


#
# Application access widget
#
class AccessWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        # %fixme rewrite
        r = ["""<style>
        .module-name {
            margin:     0;
            padding:    2px 5px 3px 5px;
            font-size:  11px;
            text-align: left;
            font-weight: bold;
            background:  #7CA0C7 url(/media/admin/img/default-bg.gif) top left repeat-x;
            color:       white;
        }

        ul.permlist {
            margin:     0;
            padding:    0;
            display:    flex;
            flex-wrap: wrap;
            list-style: none;
        }

        ul.permlist li {
            width:      120px;
            list-style: none;
            display:    table-cell;
        }

        .app-name {
            width: 200px;
            font-weight: bold;
        }

        .perm-label {
            padding-left: 4px;
        }

        .perm-title {
            display: flex;
            justify-content: space-between;
        }
        </style>
        <script>
            function resetValues(name) {
                $("."+name).prop('checked', false)
            }
        </script>
        """]
        r += ["<table width='100%'>"]
        apps = site.apps.keys()
        perms = Permission.objects.values_list("name", flat=True)
        current_perms = set()
        mode = None
        if value:
            if value.startswith("user:"):
                user = User.objects.get(username=value[5:])
                current_perms = Permission.get_user_permissions(user)
                mode = "user"
            elif value.startswith("group:"):
                group = Group.objects.get(name=value[6:])
                current_perms = Permission.get_group_permissions(group)
                mode = "group"
        for module in [m for m in settings.INSTALLED_APPS if m.startswith("noc.")]:
            mod = module[4:]
            m = __import__("noc.services.web.apps.%s" % mod, {}, {}, "MODULE_NAME")
            r += ["<tr><td colspan='3' class='module-name'><div class='perm-title'>"]
            r += ["<div>%s</div><a onclick='resetValues(\"%s\")'" % (m.MODULE_NAME, m.MODULE_NAME)]
            r += [" style='cursor:  pointer;'>reset</a></div></td></tr>"]
            for app in [app for app in apps if app.startswith(mod + ".")]:
                app_perms = sorted([p for p in perms if p.startswith(app.replace(".", ":") + ":")])
                a = site.apps[app]
                if app_perms:
                    r += ["<tr>"]
                    r += ["<td class='app-name'>%s<br/>(%s)</td>" % (a.title, app)]
                    r += ["<td><ul class='permlist'>"]
                    for p in app_perms:
                        cb = "<li><input class='%s' type='checkbox' name='perm_%s'" % (m.MODULE_NAME, p)
                        if p in current_perms:
                            cb += " checked"
                        cb += "/>"
                        r += [cb, "<span class='perm-label'>%s</span>" % p.split(":")[-1], "</li>"]
                    r += ["</ul></td><td>"]
                    # Granular access
                    if mode == "user":
                        try:
                            user_access = a.user_access_list(user)
                            if user_access:
                                r += ["<br/>".join(sorted(user_access))]
                        except Exception:
                            pass
                        try:
                            change_link = a.user_access_change_url(user)
                            if change_link:
                                r += ["<br/><a href='%s'>Change...</a>" % change_link]
                        except Exception:
                            pass
                    elif mode == "group":
                        group_access = a.group_access_list(group)
                        change_link = a.group_access_change_url(group)
                        if group_access:
                            r += ["<br/>".join(sorted(group_access))]
                        if change_link:
                            r += ["<br/><a href='%s'>Change...</a>" % change_link]
                    r += ["</td></tr>"]
        r += ["</table>"]
        return mark_safe("".join(r))
