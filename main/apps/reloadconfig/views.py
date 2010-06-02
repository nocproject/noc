# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Reload Daemons Configs
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application,HasPerm
from noc.lib.sysutils import refresh_config
##
##
##
class ReloadConfigAppplication(Application):
    ##
    ## Reload classifier config and redirect back
    ##
    def view_reload_classifer_config(self,request):
        refresh_config("noc-classifier")
        return self.response_redirect_to_referrer(request)
    view_reload_classifer_config.url=r"^classifier/$"
    view_reload_classifer_config.url_name="classifier"
    view_reload_classifer_config.access=HasPerm("reload_classifier")
    ##
    ## Reload correlator config and redirect back
    ##
    def view_reload_correlator_config(self,request):
        refresh_config("noc-correlator")
        return self.response_redirect_to_referrer(request)
    view_reload_correlator_config.url=r"^correlator/$"
    view_reload_correlator_config.url_name="correlator"
    view_reload_correlator_config.access=HasPerm("reload_correlator")
