#!/usr/bin/env python
import os,sys,site
# Adjust paths
d=os.path.dirname(sys.argv[0])
if not d:
    d=os.getcwd()
contrib=os.path.abspath(os.path.join(d,"contrib","lib"))
sys.path.insert(0,contrib)
sys.path.insert(0,os.path.abspath(os.path.join(d,"..")))
sys.path.insert(0,d)
# Install eggs from contrib/lib
site.addsitedir(contrib)

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)
from django.core.management import execute_manager

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] not in ["test","syncdb","migrate","debug-script","script-test","topo-test"]:
        # Initialize models
        os.environ["DJANGO_SETTINGS_MODULE"]="noc.settings"
        import noc.urls
    # Execute command
    execute_manager(settings)
