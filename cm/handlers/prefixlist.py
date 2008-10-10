import noc.cm.handlers
import os,logging

class Handler(noc.cm.handlers.Handler):
    name="prefix-list"
    #
    @classmethod
    def global_pull(self):
        from noc.peer.builder import build_prefix_lists
        from noc.cm.models import Object
        objects={}
        for o in Object.objects.filter(handler_class_name=self.name):
            objects[o.repo_path]=o
        logging.debug("PrefixListHandler.global_pull(): building prefix lists")
        for peering_point,pl_name,pl in build_prefix_lists():
            logging.debug("PrefixListHandler.global_pull(): writing %s/%s (%d lines)"%(peering_point.hostname,pl_name,len(pl.split("\n"))))
            path=os.path.join(peering_point.hostname,pl_name)
            if path in objects:
                o=objects[path]
                del objects[path]
            else:
                o=Object(handler_class_name=self.name,stream_url=peering_point.provision_rcmd,
                    profile_name=peering_point.type.name,repo_path=path)
                o.save()
            o.write(pl)
        for o in objects.values():
            o.delete()
        