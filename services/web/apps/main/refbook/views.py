# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.refbook application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django.shortcuts import get_object_or_404
# Django modules
from django.views.generic import list_detail
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.application import Application, view
from noc.main.models.permission import Permission
from noc.main.models.refbook import RefBook
from noc.main.models.refbookdata import RefBookData


class RefBookAppplication(Application):
    title = _("Reference Books")

    @view(url=r"^$", url_name="index",
          menu=[_("Setup"), _("Reference Books")], access="view")
    def view_index(self, request):
        """
        Render list of refbooks
        :param request:
        :return:
        """
        ref_books = RefBook.objects.filter(is_enabled=True).order_by(
            "name")
        return self.render(request, "index.html", ref_books=ref_books)

    @view(url=r"^(?P<refbook_id>\d+)/$",
          url_name="view", access="view")
    def view_view(self, request, refbook_id):
        """
        Refbook preview
        :param request:
        :param refbook_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        can_edit = (not rb.is_builtin and
                    Permission.has_perm(request.user,
                                        "main.change_refbookdata"))
        queryset = rb.refbookdata_set.all()
        # Search
        if (request.GET and
                    "query" in request.GET and request.GET["query"]):
            query = request.GET["query"]
            # Build query clause
            w = []
            p = []
            for f in rb.refbookfield_set.filter(
                    search_method__isnull=False):
                x = f.get_extra(query)
                if not x:
                    continue
                w += x["where"]
                p += x["params"]
            w = " OR ".join(["(%s)" % x for x in w])
            queryset = queryset.extra(where=["(%s)" % w], params=p)
        else:
            query = ""
            # Use generic view for final result
        return list_detail.object_list(
            request,
            queryset=queryset,
            template_name=self.get_template_path("view.html")[0],
            extra_context={"rb": rb, "can_edit": can_edit,
                           "query": query},
            paginate_by=100,
        )

    @view(url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/$",
          url_name="item", access="view")
    def view_item(self, request, refbook_id, record_id):
        """
        Item preview
        :param request:
        :param refbook_id:
        :param record_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        rbr = get_object_or_404(RefBookData, id=int(record_id),
                                ref_book=rb)
        can_edit = (not rb.is_builtin and
                    Permission.has_perm(request.user,
                                        "main.change_refbookdata"))
        return self.render(request, "item.html",
                           {"rb": rb, "record": rbr, "can_edit": can_edit})

    @view(url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/edit/$",
          url_name="edit", access="change")
    def view_edit(self, request, refbook_id, record_id=0):
        """
        Edit item
        :param request:
        :param refbook_id:
        :param record_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        rbr = get_object_or_404(RefBookData, id=int(record_id),
                                ref_book=rb)
        can_edit = (not rb.is_builtin and
                    Permission.has_perm(request.user,
                                        "main.change_refbookdata"))
        if not can_edit:
            return self.response_forbidden("Read-only refbook")
        if request.POST:  # Edit refbook
            if not can_edit:
                return self.response_forbidden("Read-only refbook")
            # Retrieve record data
            fns = [int(k[6:]) for k in request.POST.keys() if
                   k.startswith("field_")]
            data = ["" for i in range(max(fns) + 1)]
            for i in fns:
                data[i] = request.POST["field_%d" % i]
            rbr.value = data
            rbr.save()
            self.message_user(request, "Record updated successfully")
            return self.response_redirect("main:refbook:item", rb.id,
                                          rbr.id)
        return self.render(request, "edit.html",
                           {"rb": rb, "record": rbr})

    @view(url=r"^(?P<refbook_id>\d+)/(?P<record_id>\d+)/delete/$",
          url_name="delete", access="delete")
    def view_delete(self, request, refbook_id, record_id):
        """
        Delete refbook record
        :param request:
        :param refbook_id:
        :param record_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        can_edit = (not rb.is_builtin and
                    Permission.has_perm(request.user,
                                        "main.change_refbookdata"))
        if not can_edit:
            return self.response_forbidden()
        rbd = get_object_or_404(RefBookData, ref_book=rb,
                                id=int(record_id))
        rbd.delete()
        self.message_user(request, "Record deleted")
        return self.response_redirect("main:refbook:view", rb.id)

    @view(url=r"^(?P<refbook_id>\d+)/new/$", url_name="new",
          access="add")
    def view_new(self, request, refbook_id):
        """
        Create refbook record
        :param request:
        :param refbook_id:
        :return:
        """
        rb = get_object_or_404(RefBook, id=int(refbook_id))
        can_edit = (not rb.is_builtin and
                    Permission.has_perm(request.user,
                                        "main.change_refbookdata"))
        if not can_edit:
            return self.response_forbidden("Read-only refbook")
        if request.POST:  # Edit refbook
            if not can_edit:
                return self.response_forbidden("Read-only refbook")
            # Retrieve record data
            fns = [int(k[6:]) for k in request.POST.keys() if
                   k.startswith("field_")]
            data = ["" for i in range(max(fns) + 1)]
            for i in fns:
                data[i] = request.POST["field_%d" % i]
            rbr = RefBookData(ref_book=rb, value=data)
            rbr.save()
            self.message_user(request, "Record added")
            return self.response_redirect("main:refbook:item", rb.id,
                                          rbr.id)
        return self.render(request, "new.html", {"rb": rb})
