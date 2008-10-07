from django.contrib import admin
from noc.main.models import TaskSchedule

class TaskScheduleAdmin(admin.ModelAdmin):
    list_display=["periodic_name","is_enabled","run_every","timeout","retries","retry_delay","next_run","retries_left"]
    
admin.site.register(TaskSchedule, TaskScheduleAdmin)
