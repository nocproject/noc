# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Calculator application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application
from noc.main.apps.calculator.calculators import calculator_registry
##
## Register all calculators
calculator_registry.register_all()
##
## Calculator application
##
class CalculatorAppplication(Application):
    ##
    ## Calculator index
    ##
    def view_index(self,request):
        r=[(cn,c.title) for cn,c in calculator_registry.classes.items()]
        r=sorted(r,lambda x,y: cmp(x[1],y[1]))
        return self.render(request,"index.html",{"calculators":r})
    view_index.url=r"^$"
    view_index.menu="Calculators"
    view_index.access=Application.permit
    ##
    ## Calculator view
    ##
    def view_calculate(self,request,calculator):
        try:
            c=calculator_registry[calculator](self)
        except KeyError:
            return self.response_not_found("No calculator found")
        return c.render(request)
    view_calculate.url=r"^(?P<calculator>\S+)/$"
    view_calculate.access=Application.permit
