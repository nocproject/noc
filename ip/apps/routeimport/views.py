# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import Prefixes from routing tables
## @todo: VRF-aware
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django import forms
from django.forms.formsets import formset_factory
## NOC modules
from noc.lib.app.saapplication import SAApplication, HasPerm, view
from noc.peer.models import AS
from noc.ip.models import Prefix, VRF
from noc.lib.widgets import LabelWidget
from noc.lib.validators import check_prefix
from noc.lib.ip import IP


def reduce_route(task):
    """
    Reduce task for route import
    :param task:
    :return:
    """
    from noc.ip.models import VRF, Prefix
    from noc.lib.ip import IP

    vrf = VRF.get_global()
    r = {} # prefix -> (description, objects)

    for mt in task.maptask_set.filter(status="C"):
        for instance in mt.script_result:
            if instance["type"] == "ip" and instance[
                                            "forwarding_instance"] == "default":
                for iface in instance["interfaces"]:
                    if not iface["admin_status"]:
                        continue
                    for subiface in iface["subinterfaces"]:
                        if not iface["admin_status"]:
                            continue
                        if "is_ipv4" in subiface and subiface["is_ipv4"]:
                            # Get description
                            if ("description" in subiface and
                                subiface["description"]):
                                description = subiface["description"]
                            else:
                                description = iface.get("description")
                                # Check prefixes in database
                            for ipv4 in subiface["ipv4_addresses"]:
                                prefix = IP.prefix(ipv4).normalized.prefix
                                if not Prefix.objects.filter(vrf=vrf,
                                            afi="4", prefix=prefix).exists():
                                    # No prefix in database
                                    if prefix not in r:
                                        r[prefix] = [description if description else prefix,
                                            [mt.managed_object.name]]
                                    else:
                                        r[prefix][1] += [mt.managed_object.name]
    # Render template
    return r


class RouteImportAppplication(SAApplication):
    """
    Route import application
    """
    title = "Import from routing table"
    menu = "Setup | Import Connected"
    reduce_task = reduce_route
    map_task = "get_interfaces"
    timeout = 0  # Auto-detect

    class AddAddressForm(forms.Form):
        prefix = forms.CharField()
        description = forms.CharField()
        objects = forms.CharField(required=False, widget=LabelWidget)
        DELETE = forms.BooleanField(required=False)

        def clean_prefix(self):
            p = self.cleaned_data["prefix"]
            check_prefix(p)
            return p

    def render_result(self, request, result):
        """
        Display form with imported data
        :param request:
        :param result:
        :return:
        """
        initial = []
        for prefix in result:
            description, objects = result[prefix]
            initial += [{"prefix": prefix, "description": description,
                         "objects": ", ".join(objects)}]
        AddAddressFormSet = formset_factory(self.AddAddressForm, extra=0,
                                            can_delete=True)
        formset = AddAddressFormSet(initial=initial)
        return self.render(request, "found.html", formset=formset)

    @view(url=r"^submit/",
          url_name="submit",
          access=HasPerm("submit"))
    def view_submit(self, request):
        """
         Submit imported data
        :param request:
        :return:
        """
        AddAddressFormSet = formset_factory(self.AddAddressForm, extra=0,
                                            can_delete=True)
        formset = AddAddressFormSet(request.POST)
        c = 0
        if formset.is_valid():
            vrf = VRF.get_global()
            asn = AS.default_as()
            for form in formset.forms:
                if "DELETE" in form.cleaned_data and form.cleaned_data[
                                                     "DELETE"]:
                    continue
                try:
                    prefix = IP.prefix(form.cleaned_data["prefix"])
                except AttributeError:
                    continue # Empty set
                description = form.cleaned_data["description"]
                p, created = Prefix.objects.get_or_create(vrf=vrf,
                                      afi=prefix.afi,
                                      prefix=prefix.normalized.prefix,
                                      defaults={"asn": asn,
                                                "description": description})
                if created:
                    c += 1
        self.message_user(request, "%d prefixes are imported" % c)
        return self.response_redirect("ip:ipam:index")
