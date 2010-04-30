# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Reload Daemons Configs
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application
from noc.lib.sysutils import refresh_config
##
##
##
class ReloadConfigAppplication(Application):
    ##
    ## Reload noc-classifier config
    ##
    def reload_classifier_config(self):
        refresh_config("noc-classifier")
    ##
    ## Reload correlator config
    ##
    def reload_correlator_config(self):
        refresh_config("noc-correlator")
    ##
    ## Reload classifier config and redirect back
    ##
    def view_reload_classifer_config(self,request):
        self.reload_classifier_config()
        return self.response_redirect_to_referrer(request)
    view_reload_classifer_config.url=r"^classifier/$"
    view_reload_classifer_config.url_name="classifier"
    view_reload_classifer_config.access=Application.has_perm("fm.add_eventclassificationrule")
    ##
    ## Reload correlator config and redirect back
    ##
    def view_reload_correlator_config(self,request):
        self.reload_correlator_config()
        return self.response_redirect_to_referrer(request)
    view_reload_correlator_config.url=r"^correlator/$"
    view_reload_correlator_config.url_name="correlator"
    view_reload_correlator_config.access=Application.has_perm("fm.add_eventcorrelationrule")
