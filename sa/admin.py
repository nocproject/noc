from django.contrib import admin
from noc.sa.models import TaskSchedule,Activator

class ActivatorAdmin(admin.ModelAdmin):
    list_display=["name","ip","is_active"]
    
class TaskScheduleAdmin(admin.ModelAdmin):
    list_display=["periodic_name","is_enabled","run_every","timeout","retries","retry_delay","next_run","retries_left"]
    
admin.site.register(TaskSchedule, TaskScheduleAdmin)
admin.site.register(Activator,    ActivatorAdmin)

