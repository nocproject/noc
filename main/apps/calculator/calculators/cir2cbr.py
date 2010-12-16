# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## bps to burst-rate conversion
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from decimal import *
## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.utils.safestring import mark_safe
## NOC modules
from noc.main.apps.calculator.calculators import Calculator as CalculatorBase

##
## Calculator form
##
class CalculatorForm(forms.Form):
    value=forms.CharField(help_text=_("CIR(bps). K, M and G suffixes can be used"))
    Tc=forms.DecimalField(initial="0.25",
        help_text=_('Common values are: Tc=1.5 for rate-limit and Tc=0.25 for policing (0.25 is default)'))
    calculation=forms.ChoiceField(required=True,
        choices=[
            ("ios_policy",  _("Cisco IOS policer")),
            ("ios_rate",    _("Cisco IOS rate-limit")),
            ("junos_policy",_("Juniper JUNOS policer"))])
    
    MULTIPLIERS={
        "k" : 1000,
        "m" : 1000000,
        "g" : 1000000000,
    }
    ##
    ## Process K, M and G suffixes
    ##
    def clean_value(self):
        value=self.cleaned_data["value"]
        m=value[-1].lower()
        if m in self.MULTIPLIERS:
            mp=self.MULTIPLIERS[m]
            value=value[:-1]
        else:
            mp=1
        try:
            value=int(value)
        except:
            raise forms.ValidationError(_("Integer is required"))
        return value*mp

##
## Calculator
##
class Calculator(CalculatorBase):
    name="CIR2CBR"
    title=_("CIR/CAR(bps) to Burst-rate")
    description=_("Recommended way for policy-map values calculating is: normal-burst-bytes=bits-per-second*Tc/8."
            "Recommended way for rate-limit values calculating is: burst-normal=bits-per-second*Tc/8, burst-max=2*burst-normal")
    form_class=CalculatorForm
    ## Templates
    template_ios_policy="policy-map shape-%(value)d\n"\
                        "  class class-default\n"\
                        "    police %(value)d %(v)d %(v)d conform-action transmit exceed-action drop violate-action drop\n"
    template_ios_rate="rate-limit input %(value)d %(v)d %(v1)d conform-action transmit exceed-action drop"
    template_junos_policy=  "policer policer-%(value)d {\n"\
                            "    if-exceeding {\n"\
                            "        bandwidth-limit %(value)d;\n"\
                            "        burst-size-limit %(v)d;\n"\
                            "    }\n"\
                            "    then {\n"\
                            "        discard;\n"\
                            "    }\n"\
                            "}\n"
    ##
    ## Escape result
    ##
    def escape(self,s):
        return mark_safe("<pre>%s</pre>"%s)
    ##
    ## Calculate IOS policy
    ##
    def calculate_ios_policy(self,value,v):
        return [("CIR(bps)",value),
                ("normal-burst-bytes, extended-burst-bytes",v),\
                ("Policy-map example", self.escape(self.template_ios_policy%{"value":value,"v":v}))]
    
    ##
    ## Calculate IOS rate
    ##
    def calculate_ios_rate(self,value,v):
        v1=2*v
        return [("CIR(bps)",value),
                ("burst-normal",v),
                ("burst-max",v1),
                ("Rate-limit example", self.escape(self.template_ios_rate%{"value":value,"v":v,"v1":v1}))]
    
    ##
    ## Calculate Junos policy
    ##
    def calculate_junos_policy(self,value,v):
        return [("CIR(bps)",value),
                ("burst-rate",v),
                ("Policer example",self.escape(self.template_junos_policy%{"value":value,"v":v}))]
    
    ##
    ## Calculator
    ##
    def calculate(self,value,Tc,calculation):
        v=int(value*Tc/8)
        return getattr(self,"calculate_%s"%calculation)(value,v)
    
