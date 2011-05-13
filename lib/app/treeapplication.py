# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Application class
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from application import Application, view, HasPerm


class TreeApplication(Application):
    menu = None
    verbose_name = None
    verbose_name_plural = None
    model = None
    category_field = "category"  # model.category_field
    category_model = None
    parent_field = "parent"  # category_model.parent -> category_model
    
    def get_menu(self):
        return self.menu
    
    def get_children(self, parent=None, filter=None):
        def has_children(p):
            mq = self.model.objects.filter(**{self.category_field: p.id})
            if filter:
                mq = mq.filter(__raw__=filter)
            return (self.category_model.objects.filter(parent=p.id) or mq)
        
        if self.category_model:
            # Categories tree given
            if parent is None:
                for p in self.category_model.objects.filter(**{"%s__exists" % self.parent_field: False}).order_by("name"):
                    if (filter and
                        self.model.objects.filter(__raw__=filter).filter(**{self.category_field: p.id}).first() is None):
                        continue
                    yield p.id, p.name, has_children(p)
            else:
                for p in self.category_model.objects.filter(**{self.parent_field: parent}).order_by("name"):
                    if (filter and
                        self.model.objects.filter(__raw__=filter).filter(**{self.category_field: p.id}).first() is None):
                        continue
                    yield p.id, p.name.split(" | ")[-1], has_children(p)
                mq = self.model.objects.filter(**{self.category_field: parent})
                if filter:
                    mq = mq.filter(__raw__=filter)
                for p in mq.order_by("name"):
                    yield p.id, p.name.split(" | ")[-1], False
        else:
            # No categories
            mq = self.model.objects.all()
            if filter:
                mq = mq.filter(__raw__=filter)
            for p in mq.order_by("name"):
                yield p.id, p.name, False
    
    def get_object(self, object_id):
        """
        Get object by id. Return object reference or None
        
        :param object_id: Object Id
        :type object_id: Str
        :rtype: Object instance or None
        """
        return self.model.objects.filter(id=object_id).first()
    
    def render_tree_popup(self, request, lookup_url):
        """
        Render tree-stype popup
        """
        return self.render(request, "app/tree/popup_tree.html",
                           lookup_url=lookup_url)
    
    @view(url=r"lookup_tree/$", url_name="lookup_tree", access=HasPerm("view"))
    def view_lookup_tree(self, request):
        """
        AJAX handler to dynamically supply tree data
        """
        def to_json(id, title, has_children):
            d = {"data": {"title": title}, "attr": {"id": "node_"+str(id)}}
            if has_children:
                d["state"] = "closed"
                d["attr"]["rel"] = "folder"
            else:
                d["data"]["attr"] = {"href": "%s/" % id}
            return d
        
        node = None
        if request.GET and "node" in request.GET:
            node = request.GET["node"]
            if node == "root":
                node = None
        if node is None:
            data = {
                "data": self.verbose_name_plural,
                "state": "closed",
                "attr": {"id": "node_root", "rel": "root"},
                "children": [to_json(*c) for c in self.get_children()]
            }
        else:
            data = [to_json(*c) for c in self.get_children(node)]
        return self.render_json(data)
    
    @view(url=r"^$", url_name="tree", menu=get_menu, access=HasPerm("list"))
    def view_tree(self, request):
        """
        Render tree
        """
        return self.render(request, "app/tree/tree.html",
                           verbose_name=self.verbose_name)
    
    @view(url=r"^(?P<object_id>[0-9a-f]+)/$", url_name="preview",
          access=HasPerm("view"))
    def view_preview(self, request, object_id):
        """
        Render item preview
        """
        o = self.get_object(object_id)
        if not o:
            return self.response_not_found("Object not found")
        return self.render(request, "preview.html", o=o)
