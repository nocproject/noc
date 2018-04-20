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
    ##
    ## Fields to show in tree. List of dicts.
    ## Possible items of dicts are:
    ## * field (required) - DB field name
    ## * format (optional) - optional field formatting, see below
    ## * css (optional) - dict of column's CSS attributes
    ##
    ## Formats:
    ## * short - Only part right of last |
    list_display = [{"field": "name"}]  # List of field names to show
    
    def format_default(self, s):
        return s
    
    def format_short(self, s):
        return s.split(" | ")[-1]
    
    def get_menu(self):
        return self.menu
    
    def get_children(self, parent=None, filter=None):
        def has_children(p):
            mq = self.model.objects.filter(**{self.category_field: p.id})
            if filter:
                mq = mq.filter(__raw__=filter)
            return (self.category_model.objects.filter(parent=p.id) or mq)
        
        def get_descendants(parent):
            d = [parent]
            for c in self.category_model.objects.filter(**{self.parent_field: parent}):
                d += get_descendants(c.id)
            return d
        
        def s_category(c):
            return u"<span class='noc-tree-category'>%s</span>" % self.html_escape(c)
        
        def s_item(p):
            r = [u"<span class='noc-tree-item'>"]
            for i, f in enumerate(self.list_display):
                r += ["<span class='noc-tree-c%d'>" % i]
                format = getattr(self, "format_%s" % f.get("format", "default"))
                r += [self.html_escape(format(getattr(p, f["field"])))]
                r += ["</span>"]
            r += [u"</span>"]
            return "".join(r)
        
        if self.category_model:
            # Categories tree given
            if parent is None:
                for p in self.category_model.objects.filter(**{"%s__exists" % self.parent_field: False}).order_by("name"):
                    if (filter and
                        self.model.objects.filter(__raw__=filter).filter(**{self.category_field + "__in": get_descendants(p.id)}).first() is None):
                        continue
                    yield p.id, s_category("%s") % p.name, has_children(p)
            else:
                for p in self.category_model.objects.filter(**{self.parent_field: parent}).order_by("name"):
                    if (filter and
                        self.model.objects.filter(__raw__=filter).filter(**{self.category_field + "__in": get_descendants(p.id)}).first() is None):
                        continue
                    yield p.id, s_category("%s") % p.name.split(" | ")[-1], has_children(p)
                mq = self.model.objects.filter(**{self.category_field: parent})
                if filter:
                    mq = mq.filter(__raw__=filter)
                for p in mq.order_by("name"):
                    yield p.id, s_item(p), False
        else:
            # No categories
            mq = self.model.objects.all()
            if filter:
                mq = mq.filter(__raw__=filter)
            for p in mq.order_by("name"):
                yield p.id, s_item(p), False
    
    def get_object(self, object_id):
        """
        Get object by id. Return object reference or None
        
        :param object_id: Object Id
        :type object_id: Str
        :rtype: Object instance or None
        """
        return self.model.objects.filter(id=object_id).first()
    
    def get_preview_extra(self, obj):
        """
        Get additional data to preview form.
        Extra data will be available as _extra_
        """
        return {}
    
    def render_tree_popup(self, request, lookup_url,
                          css_url=None, choose_id=None):
        """
        Render tree-stype popup
        """
        if css_url is None:
            css_url = self.base_url + "css/"
        return self.render(request, "app/tree/popup_tree.html",
                           lookup_url=lookup_url, css_url=css_url,
                           choose_id=choose_id)
    
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
                "data": unicode(self.verbose_name_plural),
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
        return self.render(request, ["tree.html", "app/tree/tree.html"],
                           verbose_name=self.verbose_name)
    
    @view(url=r"^css/$", url_name="tree_css", access=HasPerm("list"))
    def view_css(self, request):
        """
        Render items' CSS
        """
        css=[]

        for n, f in enumerate(self.list_display):
            css += [".noc-tree-c%d {" % n]
            css += ["display: inline-block;"]
            if n > 0:
                css += ["padding-left: 4px;"]
                css += ["border-left: 1px solid #c0c0c0;"]
            for k, v in f.get("css", {}).items():
                css += ["    %s: %s;" % (k, v)]
            css += ["}"]
        return self.render_plain_text("\n".join(css), "text/css")
    
    @view(url=r"^(?P<object_id>[0-9a-f]{24})/$", url_name="preview",
          access=HasPerm("view"))
    def view_preview(self, request, object_id):
        """
        Render item preview
        """
        o = self.get_object(object_id)
        if not o:
            return self.response_not_found("Object not found")
        return self.render(request, "preview.html",
                           o=o, extra=self.get_preview_extra(o))

    @view(url="^popup/$", url_name="popup", access=HasPerm("view"))
    def view_popup(self, request):
        if request.GET and "choose_id" in request.GET:
            choose_id = request.GET["choose_id"]
        else:
            choose_id = None
        return self.render_tree_popup(request,
                                      self.base_url + "lookup_tree/",
                                      choose_id=choose_id)
