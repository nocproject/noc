# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Parallel command execution
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
## NOC modules
from noc.lib.app.saapplication import SAApplication
from noc.core.translation import ugettext as _


##
## Reduce task for commands
##
def reduce_commands(task, commands):
    r = [
        "<style>.cmd {border-bottom: 1px solid black;font-weight: bold;}</style>"]
    r += ["<table border='1'>",
          "<tr><th>Object</th><th>Status</th><th>Result</th></tr>"]
    for mt in task.maptask_set.all().order_by('managed_object__name'):
        if mt.status == "C":
            result = "\n".join(
                ["<div class='cmd'>%s</div><br/><pre>%s</pre><br/>" % (c, sr)
                 for c, sr in zip(commands, mt.script_result)])
        else:
            result = "<pre>%s</pre>" % str(mt.script_result)
        r += ["<tr>", "<td>", mt.managed_object.name, "</td>", "<td>",
              mt.status, "</td>", "<td>", result, "</td>", "</tr>"]
    r += ["</table>"]
    return "".join(r)


class RunCommandsApplication(SAApplication):
    title = _("Run commands")
    menu = [_("Tasks"), _("Run Commands")]
    reduce_task = reduce_commands
    map_task = "commands"
    timeout = None

    class CommandsForm(forms.Form):
        commands = forms.CharField(widget=forms.Textarea,
                                   help_text="Enter a list of commands to execute. One command per a line.")
        ignore_cli_errors = forms.BooleanField(required=False,
            help_text=_("Ignore CLI errors and continue execution"))
        batch = forms.BooleanField(
            required=False,
            help_text="Run as single command"
        )

    form = CommandsForm

    def clean_map(self, data):
        """
        Convert text field to a list of commands
        :param data:
        :return:
        """
        if data.get("batch"):
            commands = [data["commands"]]
        else:
            commands = [c for c in data["commands"].splitlines()]
        return {
            "commands": commands,
            "ignore_cli_errors": data["ignore_cli_errors"]
        }

    def clean_reduce(self, data):
        """
        Save a list of commands for reduce task
        :param data:
        :return:
        """
        return {
            "commands": [c for c in data["commands"].splitlines()]
        }
