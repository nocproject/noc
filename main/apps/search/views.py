# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Global Search
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Django Modules
from django.utils.translation import ugettext_lazy as _
from django import forms
# NOC Modules
from noc.lib.forms import NOCForm
from noc.lib.app import Application,PermitLogged,view
from noc.lib.search import search as search_engine

##
## Search engine application
##
class SearchApplication(Application):
    title="Search"
    ##
    ## Simple search form
    ##
    class SearchForm(NOCForm):
        query=forms.CharField(label=_("Query"))
    
    ##
    ## Render success page
    ##
    @view(url=r"^$", url_name="search", access=PermitLogged())
    def view_search(self,request):
        result=[]
        rq = request.POST or request.GET
        if rq:
            form=self.SearchForm(rq)
            if form.is_valid():
                result=search_engine(request.user,form.cleaned_data["query"])
        else:
            form=self.SearchForm()
        return self.render(request,"search.html",{"form":form,"result":result})
    
