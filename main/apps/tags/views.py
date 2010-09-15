# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tags application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application,PermitLogged
from tagging.models import Tag
from tagging.utils import calculate_cloud
from django.shortcuts import get_object_or_404
import math

class TagWrapper: pass
##
##
##
class TagsAppplication(Application):
    title="Tags"
    ##
    ## Tags cloud
    ##
    def view_index(self,request):
        MIN_FONT=6
        MAX_FONT=36
        # Get tags and counts
        tags=[r for r in self.execute("""
            SELECT t.name,COUNT(*)
            FROM tagging_tag t JOIN tagging_taggeditem i ON (t.id=i.tag_id)
            GROUP BY 1
            ORDER BY 1""")]
        # Build cloud
        if tags:
            # Get min and max count
            counts=[r[1] for r in tags]
            min_count=min(counts)
            max_count=max(counts)
            # Calculate font size
            if min_count==max_count:
                # Set minimal font size if all tags of equal power
                tags=[(r[0],MIN_FONT) for r in tags]
            else:
                s=float(MAX_FONT-MIN_FONT)/math.log(max_count)
                tags=[(r[0],int(MIN_FONT+s*math.log(r[1]))) for r in tags]
        return self.render(request,"index.html",{"tags":tags})
    view_index.url=r"^$"
    view_index.url_name="index"
    view_index.menu="Tags"
    view_index.access=PermitLogged()
    ##
    ## Display all objects belonging to tag
    ##
    def view_tag(self,request,tag):
        t=get_object_or_404(Tag,name=tag)
        items={} # Type -> itemlist
        for i in t.items.all():
            if i.object is None:
                continue
            itype=i.object.__class__._meta.verbose_name_plural
            if itype in items:
                items[itype]+=[i.object]
            else:
                items[itype]=[i.object]
        items=sorted(items.items(),lambda x,y:cmp(x[0],y[0]))
        return self.render(request,"tag.html",{"tag":t,"items":items})
    view_tag.url=r"^(?P<tag>.+)/$"
    view_tag.url_name="tag"
    view_tag.access=PermitLogged()
    ##
    ## AJAX lookup
    ##
    def view_lookup(self,request):
        def lookup_function(q):
            for m in Tag.objects.filter(name__istartswith=q):
                yield m.name
        return self.lookup_json(request,lookup_function)
    view_lookup.url=r"^lookup/$"
    view_lookup.url_name="lookup"
    view_lookup.access=PermitLogged()

