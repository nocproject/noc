# ---------------------------------------------------------------------
# Parallel command execution
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extapplication import ExtApplication
from noc.services.web.base.application import view
from noc.core.translation import ugettext as _
from noc.core.models.valuetype import ValueType
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.commandsnippet import CommandSnippet
from noc.sa.models.action import Action
from noc.sa.interfaces.base import ListOfParameter, ModelParameter, DictParameter


class RunCommandsApplication(ExtApplication):
    title = _("Run Commands")
    menu = [_("Run Commands (On Group Edit option)")]

    implied_permissions = {"launch": ["sa:objectlist:read"]}

    def get_launch_info(self, request):
        """
        Return Alias to ManagedObject
        """

        return {
            "class": "NOC.sa.managedobject.Application",
            "title": self.title,
            "params": {
                "url": self.menu_url,
                "permissions": ["read", "commands"],
                "app_id": self.app_id,
                "link": None,
            },
        }

    @view(url=r"^form/snippet/(?P<snippet_id>\d+)/$", method=["GET"], access="launch", api=True)
    def api_form_snippet(self, request, snippet_id):
        snippet = self.get_object_or_404(CommandSnippet, id=int(snippet_id))
        r = []
        vars = snippet.vars
        for k in vars:
            cfg = {"name": k, "fieldLabel": k, "allowBlank": not vars[k].get("required", False)}
            t = vars[k].get("type")
            if t == "int":
                cfg["xtype"] = "numberfield"
            else:
                cfg["xtype"] = "textfield"
            r += [cfg]
        return r

    @view(
        url=r"^form/action/(?P<action_id>[0-9a-f]{24})/$", method=["GET"], access="launch", api=True
    )
    def api_form_action(self, request, action_id):
        action = self.get_object_or_404(Action, id=action_id)
        r = []
        for p in action.params:
            cfg = {
                "name": p.name,
                "fieldLabel": p.description or p.name,
                "allowBlank": not p.is_required,
            }
            if p.type in (ValueType.INTEGER, ValueType.VLAN):
                cfg["xtype"] = "numberfield"
            else:
                cfg["xtype"] = "textfield"
            r += [cfg]
        return r

    @view(
        url=r"^render/snippet/(?P<snippet_id>\d+)/$",
        method=["POST"],
        validate={
            "objects": ListOfParameter(element=ModelParameter(ManagedObject)),
            "config": DictParameter(),
        },
        access="launch",
        api=True,
    )
    def api_render_snippet(self, request, snippet_id, objects, config):
        snippet = self.get_object_or_404(CommandSnippet, id=int(snippet_id))
        r = {}
        for mo in objects:
            config["object"] = mo
            r[mo.id] = snippet.expand(config)
        return r

    @view(
        url=r"^render/action/(?P<action_id>[0-9a-f]{24})/$",
        method=["POST"],
        validate={
            "objects": ListOfParameter(element=ModelParameter(ManagedObject)),
            "config": DictParameter(),
        },
        access="launch",
        api=True,
    )
    def api_render_action(self, request, action_id, objects, config):
        action = self.get_object_or_404(Action, id=action_id)
        r = {}
        # as job - 202 Accepted
        for mo in objects:
            match = mo.get_matcher_ctx()
            try:
                commands = action.render_commands(
                    mo.profile,
                    match_ctx=match,
                    managed_object=mo,
                    **config,
                )
            except ValueError as e:
                return self.render_json(
                    {"status": False, "message": str(e)}, status=self.BAD_REQUEST
                )
            r[mo.id] = "\n".join(commands)
        # Register Audit
        return r
