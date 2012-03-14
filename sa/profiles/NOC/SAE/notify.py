# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.notify
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC module
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import INotifySAE
from noc.sa.protocols.sae_pb2 import RefreshObjectMappingsRequest


class Script(NOCScript):
    name = "NOC.SAE.notify"
    implements = [INotifySAE]
    
    def empty_callback(self, transaction,response=None,error=None):
        pass
    
    def refresh_object_mappings(self, object_id):
        """
        Send refresh_object_mappings messages
        To all activators serving managed object
        """
        from noc.sa.models import ManagedObject
        
        self.debug("Requesting event filter refresh")
        o = ManagedObject.objects.get(id=object_id)
        a_name = o.activator.name
        if a_name in self.sae.activators:
            r = RefreshObjectMappingsRequest()
            for a in self.sae.activators[a_name]:
                self.debug("Requesting refresh on %r" % a)
                a.proxy.refresh_object_mappings(r, self.empty_callback)
        return True
    
    def execute(self, event, **kwargs):
        self.debug("Event: %s" % event)
        if event == "refresh_object_mappings" and "object_id" in kwargs:
            return self.refresh_object_mappings(kwargs["object_id"])
