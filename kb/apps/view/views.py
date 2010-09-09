# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Knowledge Base viewer
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.shortcuts import get_object_or_404
from noc.lib.app import Application,HasPerm
from noc.kb.models import KBEntry,KBEntryAttachment
from noc.main.models import MIMEType
##
## View application
##
class ViewAppplication(Application):
    title="View"
    ##
    ## Index page must redirect to index application
    ##
    def view_index(self,request):
        return self.response_redirect("kb:index:index")
    view_index.url=r"^$"
    view_index.url_name="index"
    view_index.access=HasPerm("view")
    ##
    ## KB Entry Preview
    ##
    def view_view(self,request,kb_id):
        e=get_object_or_404(KBEntry,id=int(kb_id))
        e.log_preview(request.user)
        return self.render(request,"view.html",{"e":e,"has_bookmark":e.is_bookmarked(request.user)})
    view_view.url=r"^(?P<kb_id>\d+)/$"
    view_view.url_name="view"
    view_view.access=HasPerm("view")
    ##
    ## Download attachment
    ##
    def view_attachment(self,request,kb_id,name):
        e=get_object_or_404(KBEntry,id=int(kb_id))
        a=get_object_or_404(KBEntryAttachment,kb_entry=e,name=name)
        return self.render_response(a.file.file.read(),content_type=MIMEType.get_mime_type(a.file.name))
    view_attachment.url=r"^(?P<kb_id>\d+)/attachment/(?P<name>.+)/$"
    view_attachment.url_name="attachment"
    view_attachment.access=HasPerm("view")
    ##
    ## Manipulate user bookmark
    ##     action is one of "set" or "unset"
    def view_bookmark(self,request,kb_id,action):
        if action not in ("set","unset"):
            return self.response_not_found()
        e=get_object_or_404(KBEntry,id=int(kb_id))
        if action=="set":
            e.set_user_bookmark(request.user)
        else:
            e.unset_user_bookmark(request.user)
        return self.response_redirect_to_referrer(request)
    view_bookmark.url=r"(?P<kb_id>\d+)/bookmark/(?P<action>set|unset)/$"
    view_bookmark.url_name="bookmark"
    view_bookmark.access=HasPerm("view")
