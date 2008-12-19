##
## Backup database to main.backupdir
## TODO:
##      * Remove backup when pg_dump failed
##      * Provide pg_dump with password when requred
##      * Remove old dumps
##
import noc.sa.periodic
from noc.settings import config
import os,subprocess,datetime
import logging

class Task(noc.sa.periodic.Task):
    name="main.cleanup_sessions"
    description=""
    
    def execute(self):
        from django.db import connection
        cursor=connection.cursor()
        cursor.execute("DELETE FROM django_session WHERE expire_date<'now'")
        cursor.execute("COMMIT")
        return True
