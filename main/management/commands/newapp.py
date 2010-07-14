# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Create application skeleton
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand,CommandError
from optparse import make_option
import os

VIEWS_SKELETON="""# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## <<DESCRIPTION>>
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app import Application
##
##
##
class TheAppplication(Application):
    pass
"""

MODEL_VIEWS_SKELETON="""# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## %(model)s Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.%(module)s.models import %(model)s
##
## %(model)s admin
##
class %(model)sAdmin(admin.ModelAdmin):
    pass
##
## %(model)s application
##
class %(model)sApplication(ModelApplication):
    model=%(model)s
    model_admin=%(model)sAdmin
    menu="Setup | %(model)s"
"""

SIMPLE_REPORT_VIEWS_SKELETON="""# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## %(app)s Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
##
##
##
class Report%(app)s(SimpleReport):
    title="%(app)s"
    def get_data(self,**kwargs):
        return self.from_dataset(title=self.title,columns=[],data=[])
"""

APPLICATION_TEST_CASE="""# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## %(app)s Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase

class %(app)sTestCase(ApplicationTestCase):
    pass
"""

MODEL_APPLICATION_TEST_CASE="""# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## %(app)s Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelApplicationTestCase

class %(app)sTestCase(ModelApplicationTestCase):
    pass
"""

REPORT_APPLICATION_TEST_CASE="""# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## %(app)s Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ReportApplicationTestCase

class %(app)sTestCase(ReportApplicationTestCase):
    pass
"""

##
## Initialize application skeleton
##
class Command(BaseCommand):
    help="Create application skeleton"
    option_list=BaseCommand.option_list+(
        make_option("--model","-m",dest="model",help="Create ModelApplication"),
        make_option("--report","-r",dest="report",help="Create Report"),
    )
    def handle(self, *args, **options):
        for app in args:
            print "Creating skeleton for %s"%app
            m,a=app.split(".")
            app_path=os.path.join(m,"apps",a)
            template_path=os.path.join(app_path,"templates")
            if not os.path.exists(template_path):
                os.makedirs(template_path)
            init=os.path.join(m,"apps","__init__.py")
            if not os.path.exists(init):
                with open(init,"w"):
                    pass
            init=os.path.join(app_path,"__init__.py")
            if not os.path.exists(init):
                with open(init,"w"):
                    pass
            views=os.path.join(app_path,"views.py")
            if not os.path.exists(views):
                if "model" in options and options["model"]:
                    v=MODEL_VIEWS_SKELETON%{"model":options["model"],"module":m}
                elif "report" in options and options["report"]:
                    if options["report"]=="simple":
                        v=SIMPLE_REPORT_VIEWS_SKELETON%{"app":a}
                    else:
                        raise Exception("Invalid report type")
                else:
                    v=VIEWS_SKELETON
                with open(views,"w") as f:
                    f.write(v)
            tests=os.path.join(app_path,"tests")
            if not os.path.exists(tests):
                os.makedirs(tests)
            init=os.path.join(tests,"__init__.py")
            if not os.path.exists(init):
                with open(init,"w"):
                    pass
            app_test=os.path.join(tests,"test.py")
            if not os.path.exists(app_test):
                if "model" in options and options["model"]:
                    v=MODEL_APPLICATION_TEST_CASE%{"app":a}
                elif "report" in options and options["report"]:
                    v=REPORT_APPLICATION_TEST_CASE%{"app":a}
                else:
                    v=APPLICATION_TEST_CASE%{"app":a}
                with open(app_test,"w") as f:
                    f.write(v)
                
