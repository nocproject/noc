# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Active Problems application
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application,HasPerm
##
## Active Problems
##
class ActiveProblemsAppplication(Application):
    title="Active problems"
    ##
    ## Display summary page
    ##
    def view_summary(self,request):
        cursor=self.cursor()
        cursor.execute("""SELECT o.name AS object_name,ec.name AS class_name,ep.name AS priority_name,COUNT(*) AS count
        FROM fm_event e JOIN sa_managedobject o ON (e.managed_object_id=o.id)
            JOIN fm_eventclass ec ON (ec.id=e.event_class_id)
            JOIN fm_eventpriority ep ON (e.event_priority_id=ep.id)
        WHERE
            e.status='A' AND ep.priority>1000
        GROUP BY 1,2,3
        ORDER BY 1,3,2,4 DESC
        """)
        data=cursor.fetchall()
        return self.render(request,"summary.html",{"data":data})
    view_summary.url=r"^/"
    view_summary.access=HasPerm("view")
    view_summary.menu="Active Problems"

