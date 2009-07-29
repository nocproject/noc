# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## "now"search"" macro
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.kb.parsers.macros import Macro as MacroBase
from django.db.models import Q
##
## "search" macro
## USAGE:
## <<search [criteria] [order_by] [limit] [title]>>
## WHERE:
##     criteria:
##         category=cat1,...,catN
##         language=lang
##     order_by - one of "subject","-subject","id","-id"
##     limit
##     title - table title
##     display_list - list of fields ("id","subject")
##
class Macro(MacroBase):
    name="search"
    @classmethod
    def handle(cls,args,text):
        from noc.kb.models import KBEntry
        # Build search criteria
        if "category" in args:
            q=Q()
            for cn in args["category"].split(","):
                cn=cn.strip()
                q&=Q(categories__name=cn)
        else:
            q=Q()
        if "language" in args:
            q&=Q(language__name=args["language"])
        q=KBEntry.objects.filter(q) # Flatten to query
        # Apply ordering
        if "order_by" in args:
            if args["order_by"] not in ["subject","-subject","id","-id"]:
                raise Exception("Invalid order_by value")
            q=q.order_by(args["order_by"])
        # Apply limition
        if "limit" in args:
            q=q[:int(args["limit"])]
        # Build display list
        if "display_list" in args:
            display_list=[]
            for f in args["display_list"].split(","):
                f=f.strip()
                if f not in ("id","subject"):
                    raise Exception("Invalid field %s"%f)
                display_list.append(f)
        else:
            display_list=["id","subject"]
        # Render
        out=["<table border='0'>"]
        if "title" in args:
            out+=["<tr><th>%s</th></tr>"%args["title"]]
        for a in q:
            link="/kb/%d/"%a.id
            out+=["<tr>"]
            for f in display_list:
                if f=="id":
                    out+=["<td><a href='%s'>KB%s</a></td>"%(link,getattr(a,f))]
                else:
                    out+=["<td><a href='%s'>%s</a></td>"%(link,getattr(a,f))]
            out+=["</tr>"]
        out+=["</table>"]
        return u"\n".join(out)
