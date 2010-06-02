# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## <<DESCRIPTION>>
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.views.generic import list_detail
from django.shortcuts import get_object_or_404
from noc.lib.app import Application,HasPerm
from noc.main.models import *
##
##
##
class RefBookAppplication(Application):
    title="Reference Books"
    ##
    ## Render list of refbooks
    ##
    def view_index(self,request):
        ref_books=RefBook.objects.filter(is_enabled=True).order_by("name")
        return self.render(request,"index.html",{"ref_books":ref_books})
    view_index.url=r"^$"
    view_index.url_name="index"
    view_index.menu="Reference Books"
    view_index.access=HasPerm("view")
    ##
    ## Refbook preview
    ##
    def view_view(self,request,refbook_id):
        rb=get_object_or_404(RefBook,id=int(refbook_id))
        can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
        queryset=rb.refbookdata_set.all()
        # Search
        if request.GET and request.GET.has_key("query") and request.GET["query"]:
            query=request.GET["query"]
            # Build query clause
            w=[]
            p=[]
            for f in rb.refbookfield_set.filter(search_method__isnull=False):
                x=f.get_extra(query)
                if not x:
                    continue
                w+=x["where"]
                p+=x["params"]
            w=" OR ".join(["(%s)"%x for x in w])
            queryset=queryset.extra(where=["(%s)"%w],params=p)
        else:
            query=""
        # Use generic view for final result
        return list_detail.object_list(
            request,
            queryset=queryset,
            template_name=self.get_template_path("view.html")[0],
            extra_context={"rb":rb,"can_edit":can_edit,"query":query},
            paginate_by=100,
        )
    view_view.url=r"^(?P<refbook_id>\d+)/$"
    view_view.url_name="view"
    view_view.access=HasPerm("view")
    ##
    ## Item preview
    ##
    def view_item(self,request,refbook_id,record_id):
        rb=get_object_or_404(RefBook,id=int(refbook_id))
        rbr=get_object_or_404(RefBookData,id=int(record_id),ref_book=rb)
        can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
        return self.render(request,"item.html",{"rb":rb,"record":rbr,"can_edit":can_edit})
    view_item.url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/$"
    view_item.url_name="item"
    view_item.access=HasPerm("view")
    ##
    ## Edit item
    ##
    def view_edit(self,request,refbook_id,record_id=0):
        rb=get_object_or_404(RefBook,id=int(refbook_id))
        rbr=get_object_or_404(RefBookData,id=int(record_id),ref_book=rb)
        can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
        if not can_edit:
            return self.response_forbidden("Read-only refbook")
        if request.POST: # Edit refbook
            if not can_edit:
                return self.response_forbidden("Read-only refbook")
            # Retrieve record data
            fns=[int(k[6:]) for k in request.POST.keys() if k.startswith("field_")]
            data=["" for i in range(max(fns)+1)]
            for i in fns:
                data[i]=request.POST["field_%d"%i]
            rbr.value=data
            rbr.save()
            self.message_user(request,"Record updated successfully")
            return self.response_redirect("main:refbook:item",rb.id,rbr.id)
        return self.render(request,"edit.html",{"rb":rb,"record":rbr})
    view_edit.url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/edit/$"
    view_edit.url_name="edit"
    view_edit.access=HasPerm("change")
    ##
    ## Delete refbook record
    ##
    def view_delete(self,request,refbook_id,record_id):
        rb=get_object_or_404(RefBook,id=int(refbook_id))
        can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
        if not can_edit:
            return self.response_forbidden()
        rbd=get_object_or_404(RefBookData,ref_book=rb,id=int(record_id))
        rbd.delete()
        self.message_user(request,"Record deleted")
        return self.response_redirect("main:refbook:view",rb.id)
    view_delete.url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/delete/$"
    view_delete.url_name="delete"
    view_delete.access=HasPerm("delete")
    ##
    ## Create refbook record
    ##
    def view_new(self,request,refbook_id):
        rb=get_object_or_404(RefBook,id=int(refbook_id))
        can_edit=not rb.is_builtin and request.user.has_perm("main.change_refbookdata")
        if not can_edit:
            return self.response_forbidden("Read-only refbook")
        if request.POST: # Edit refbook
            if not can_edit:
                return self.response_forbidden("Read-only refbook")
            # Retrieve record data
            fns=[int(k[6:]) for k in request.POST.keys() if k.startswith("field_")]
            data=["" for i in range(max(fns)+1)]
            for i in fns:
                data[i]=request.POST["field_%d"%i]
            rbr=RefBookData(ref_book=rb,value=data)
            rbr.save()
            self.message_user(request,"Record added")
            return self.response_redirect("main:refbook:item",rb.id,rbr.id)
        return self.render(request,"new.html",{"rb":rb})
    view_new.url=r"^(?P<refbook_id>\d+)/new/$"
    view_new.url_name="new"
    view_new.access=HasPerm("add")
