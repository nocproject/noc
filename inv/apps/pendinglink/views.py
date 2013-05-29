# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.pendinglink application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.pendinglinkcheck import PendingLinkCheck
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface


class PendingLinkCheckApplication(ExtDocApplication):
    """
    PendingLinkCheck application
    """
    title = "PendingLinkCheck"
    menu = "Pending Links"
    model = PendingLinkCheck

    def field_local_object(self, obj):
        return obj.local_object.name

    def field_remote_object(self, obj):
        return obj.remote_object.name

    def get_interface_by_name(self, object, name):
        """
        Find interface by name
        :param object: Managed Object
        :param name: interface name
        :return: Interface instance or None
        """
        i = Interface.objects.filter(
            managed_object=object.id, name=name).first()
        if not i:
            # JUNOS names fixup
            si = list(SubInterface.objects.filter(
                managed_object=object.id, name=name))
            if len(si) == 1:
                i = si[0].interface
        return i

    def submit_link(self, local_object, local_interface,
                    remote_object, remote_interface, method):
        """
        Submit link to the database
        :param local_object:
        :param local_interface:
        :param remote_object:
        :param remote_interface:
        :param method:
        :return: (result, error message)
        """
        l_iface = self.get_interface_by_name(
            local_object, local_interface)
        if not l_iface:
            return False, "Interface is not found: %s:%s" % (
                local_object.name, local_interface)
        r_iface = self.get_interface_by_name(
            remote_object, remote_interface)
        if not r_iface:
            return False, "Interface is not found: %s:%s" % (
                remote_object.name, remote_interface)
        try:
            l_iface.link_ptp(r_iface, method=method)
        except ValueError, why:
            return False, "Linking error: %s" % why
        return True, "Linked"

    @view(url=r"^(?P<link_id>[0-9a-zA-Z]{24})/approve/$",
          method=["POST"], access="read", api=True)
    def api_approve(self, request, link_id):
        """
        Manually approve the link
        :param request:
        :param link_id:
        :return: True or False depending on operation result
        """
        plc = PendingLinkCheck.objects.filter(id=link_id)
        if plc:
            plc = plc[0]
        method = plc.method
        if method:
            method += "+manual"
        else:
            method = "manual"
        result, msg = self.submit_link(
            plc.local_object, plc.local_interface,
            plc.remote_object, plc.remote_interface, method)
        if result:
            # Confirmed
            plc.delete()
        return {
            "result": result,
            "msg": msg
        }
