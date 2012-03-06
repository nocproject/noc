# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Tags application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import math
## Django modules
from django.utils.encoding import smart_str
## Third-party modules
from tagging.models import Tag
from tagging.utils import calculate_cloud
## NOC modules
from noc.lib.app import Application, PermitLogged, view


class TagsAppplication(Application):
    title = "Tags"

    @view(url=r"^$", url_name="index", menu="Tags", access="launch")
    def view_index(self, request):
        """
        Tags cloud
        """
        MIN_FONT = 6
        MAX_FONT = 36
        # Get tags and counts
        tags = [r for r in self.execute("""
            SELECT t.name,COUNT(*)
            FROM tagging_tag t JOIN tagging_taggeditem i ON (t.id=i.tag_id)
            GROUP BY 1
            ORDER BY 1""")]
        # Build cloud
        if tags:
            # Get min and max count
            counts = [r[1] for r in tags]
            min_count = min(counts)
            max_count = max(counts)
            # Calculate font size
            if min_count == max_count:
                # Set minimal font size if all tags of equal power
                tags = [(r[0], MIN_FONT) for r in tags]
            else:
                s = float(MAX_FONT - MIN_FONT) / math.log(max_count)
                tags = [(r[0], int(MIN_FONT + s * math.log(r[1])))
                    for r in tags]
        return self.render(request, "index.html", tags=tags)

    @view(url=r"^(?P<tag>.+)/$", url_name="tag", access=PermitLogged())
    def view_tag(self, request, tag):
        """
        Display all objects belonging to tag
        """
        def lookup_function(q):
            for m in Tag.objects.filter(name__istartswith=q):
                yield m.name
        if tag == "lookup":
            return self.lookup_json(request, lookup_function)

        t = self.get_object_or_404(Tag, name=smart_str(tag))
        items = {}  # Type -> itemlist
        for i in t.items.all():
            if i.object is None:
                continue
            itype = i.object.__class__._meta.verbose_name_plural
            if itype in items:
                items[itype] += [i.object]
            else:
                items[itype] = [i.object]
        items = sorted(items.items(), key=lambda x: x[0])
        return self.render(request, "tag.html", tag=t, items=items)
