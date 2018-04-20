# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Set untagged ports
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
## NOC modules
from noc.lib.app.saapplication import SAApplication


def reduce_untagged(task):
    """
    Reduce task for Set Untagged
    :param task:
    :return:
    """
    result = []
    for mt in task.maptask_set.all():
        r = mt.script_result
        if mt.status == "C":
            status = "OK" if r["status"] else "ERROR"
            result += ["<b>%s: %s</b>" % (mt.managed_object.name, status)]
            result += ["<br/><pre>%s</pre>" % r["log"]]
        else:
            result += ["<b>%s: FAILED</b>" % mt.managed_object.name]
            result += ["<br/><pre>%s</pre>" % r["text"]]
    return " ".join(result)


class SetUntaggedApplication(SAApplication):
    title = "Set Untagged"
    menu = "Tasks | Set Untagged"
    reduce_task = reduce_untagged
    map_task = "set_switchport"

    class SetUntaggedForm(forms.Form):
        vlan = forms.IntegerField()
        interfaces = forms.CharField(
            help_text="Comma-separated list of interfaces")

        def clean_interfaces(self):
            interfaces = [x.strip() for x in
                          self.cleaned_data["interfaces"].split(",") if
                          x.strip()]
            return interfaces

    form = SetUntaggedForm

    def clean_map(self, data):
        """
        Populate set_switchport parameters
        :param data:
        :return:
        """
        vlan = data["vlan"]
        return {
            "protect_switchport": True,
            "protect_type": True,
            "debug": False,
            "configs": [
                {
                    "interface": i,
                    "status": True,
                    "edge_port": True,
                    "untagged": vlan
                } for i in data["interfaces"]
            ]
        }
