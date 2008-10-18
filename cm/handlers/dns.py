import noc.cm.handlers
from noc.lib.fileutils import is_differ
import os,logging

class Handler(noc.cm.handlers.Handler):
    name="dns"
    #
    @classmethod
    def global_pull(self):
        from noc.dns.models import DNSZone,DNSServer
        from noc.cm.models import Object
        
        objects={}
        changed={}
        for o in Object.objects.filter(handler_class_name=self.name).exclude(repo_path__endswith="autozones.conf"):
            objects[o.repo_path]=o
        for z in DNSZone.objects.filter(is_auto_generated=True):
            for ns in z.profile.masters.all():
                path=os.path.join(ns.name,z.name)
                if path in objects:
                    o=objects[path]
                    del objects[path]
                else:
                    logging.debug("DNSHandler.global_pull: Creating object %s"%path)
                    o=Object(handler_class_name=self.name,stream_url="ssh://u:p@localhost/",
                        profile_name="file",repo_path=path)
                    o.save()
                if is_differ(o.path,z.zonedata(ns)):
                    changed[z]=None
        for o in objects.values():
            logging.debug("DNSHandler.global_pull: Deleting object: %s"%o.repo_path)
            o.delete()
        for z in changed:
            logging.debug("DNSHandler.global_pull: Zone %s changed"%z.name)
            z.serial=z.next_serial
            z.save()
            for ns in z.profile.masters.all():
                path=os.path.join(ns.name,z.name)
                o=Object.objects.get(handler_class_name=self.name,repo_path=path)
                o.write(z.zonedata(ns))
        for ns in DNSServer.objects.all():
            logging.debug("DNSHandler.global_pull: Includes for %s rebuilded"%ns.name)
            g=ns.generator_class()
            path=os.path.join(ns.name,"autozones.conf")
            try:
                o=Object.objects.get(handler_class_name=self.name,repo_path=path)
            except Object.DoesNotExist:
                o=Object(handler_class_name=self.name,stream_url="ssh://u:p@localhost/",
                    profile_name="file",repo_path=path)
                o.save()
            o.write(g.get_include(ns))
            
    @classmethod
    def global_push(self):
        from noc.dns.models import DNSZone
        nses={}
        for z in DNSZone.objects.filter(is_auto_generated=True):
            for ns in z.profile.masters.all():
                nses[ns.name]=ns
        for ns in nses.values():
            logging.debug("DNSHandler.global_push: provisioning %s"%ns.name)
            ns.provision_zones()
