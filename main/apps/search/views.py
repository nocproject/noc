# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Global Search
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django import forms
from noc.lib.app import Application
from noc.main.search import search as search_engine
##
## Simple search form
##
class SearchForm(forms.Form):
    query=forms.CharField()
##
## Search engine application
##
class SearchApplication(Application):
    title="Search"
    ##
    ## Render success page
    ##
    def view_search(self,request):
        result=[]
        if request.POST:
            form=SearchForm(request.POST)
            if form.is_valid():
                result=search_engine(request.user,form.cleaned_data["query"])
        else:
            form=SearchForm()
        return self.render(request,"search.html",{"form":form,"result":result})
    view_search.url=r"^$"
    view_search.url_name="search"
    view_search.access=Application.permit_logged
