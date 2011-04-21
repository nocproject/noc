# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.contrib import admin
## NOC modules
from noc.cm.repoapp import RepoApplication, HasPerm, ModelApplication, view
from noc.cm.models import Config
from noc.sa.models import ReduceTask
from noc.lib.app.site import site

##
## Change link wrapper
##
def change_link(obj):
    return "<a href='%s' class='changelink'>Change</a>"%site.reverse("cm:config:change",obj.id)
change_link.short_description="Change"
change_link.allow_tags=True

##
## Reduce task for get_now
## Returns [(managed_object, status)]
##
def reduce_get_now(task):
    from noc.lib.app import site
    import datetime
    from noc.lib.dateutils import humanize_distance
    
    now = datetime.datetime.now()
    r = []
    for mt in task.maptask_set.all():
        # Save config
        c = mt.managed_object.config
        if mt.status == "C":
            c.write(mt.script_result)
            if c.pull_every:
                c.next_pull = now + datetime.timedelta(seconds=c.pull_every)
            c.save()
        # Build result
        cfg_link = None
        diff_link = None
        diff_text = None
        if mt.managed_object.config and mt.managed_object.config.in_repo:
            cfg_link = site.reverse("cm:config:view",
                                    mt.managed_object.config.id)
            revs = list(c.revisions)
            if len(revs)>1:
                r0 = revs[0]
                r1 = revs[1]
                diff_link = site.reverse("cm:config:diff_rev",
                    mt.managed_object.config.id, "u", r1.revision, r0.revision)
                now = datetime.datetime.now()
                diff_text = "Changes from %s to %s" % (
                        humanize_distance(r1.date),
                        humanize_distance(r0.date))
        r += [(mt.managed_object, mt.status == "C", cfg_link,
              diff_link, diff_text)]
    r = sorted(r, lambda x, y: cmp(x[0].name, y[0].name))
    return r

##
## Config admin
##
class ConfigAdmin(admin.ModelAdmin):
    list_display=["repo_path", "pull_every", "last_modified", "last_pull",
                  "next_pull", "status", change_link]
    list_filter = ["managed_object__administrative_domain"]
    search_fields=["repo_path"]
    actions=["get_now"]
    def queryset(self,request):
        return Config.queryset(request.user)
    
    ##
    ## Pull objects immediately
    ##
    def get_now(self, request, queryset):
        objects = [o.managed_object for o in queryset]
        task = ReduceTask.create_task(objects,
            reduce_get_now, {},
            "get_config", {}, 120)  # @todo: make configurable
        return self.app.response_redirect("cm:config:get_now", task.id)
    
    ##
    ## Delele "delete_selected"
    ##
    def get_actions(self,request):
        actions=super(ConfigAdmin,self).get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
    

##
## Config application
##
class ConfigApplication(RepoApplication):
    repo="config"
    model=Config
    model_admin=ConfigAdmin
    menu="Configs"
    ##
    ## cm:config:change handler
    ##
    @view(url=r"^(?P<object_id>\d+)/change/$",
          url_name="change", access=HasPerm("change_settings"))
    def view_change_settings(self,request,object_id):
        def response_change(*args):
            self.message_user(request,"Parameters was changed successfully")
            return self.response_redirect("cm:config:changelist")
        self.admin.response_change=response_change
        return ModelApplication.view_change(self,request,object_id)
    
    ##
    ##
    ##
    @view(url=r"^get_now/(?P<task_id>\d+)/$",
        url_name="get_now", access=HasPerm("get_now"))
    def view_get_now(self, request, task_id):
        task = self.get_object_or_404(ReduceTask, id=int(task_id))
        try:
            result = task.get_result(block=False)
        except ReduceTask.NotReady:
            total_tasks=task.maptask_set.count()
            complete_task = task.maptask_set.filter(status="C").count()
            progress = float(complete_task) * 100.0 / float(total_tasks)
            return self.render_wait(request, subject="Pulling configs",
                                    text="Pulling configs, please wait",
                                    progress=progress)
        return self.render(request, "get_now.html", result=result)
    
    ##
    ## Disable delete
    ##
    def has_delete_permission(self,request,obj=None):
        return False
    
    ##
    ## Disable add
    ##
    def has_add_permission(self,request):
        return False
    
    ##
    ## Config highlight
    ##
    def render_content(self,object,content):
        content=unicode(content, "utf8")
        return object.managed_object.profile.highlight_config(content)
    
