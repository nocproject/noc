from noc.cm.handlers import BaseHandler
import os

class Handler(BaseHandler):
    name="prefix-list"
    #
    @classmethod
    def global_pull(self):
        from noc.peer.builder import build_prefix_lists
        from noc.cm.models import Object
        objects={}
        for o in Object.objects.filter(handler_class_name=self.name):
            objects[o.repo_path]=o
        for peering_point,pl_name,pl in build_prefix_lists():
            path=os.path.join(peering_point.hostname,pl_name)
            if path in objects:
                o=objects[path]
                del objects[path]
            else:
                o=Object(handler_class_name="prefix-list",stream_url=peering_point.provision_rcmd,
                    profile_name=peering_point.type.name,repo_path=path)
                o.save()
            o.write(pl)
        for o in objects.values():
            o.delete()
        