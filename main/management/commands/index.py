# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Full-text search index management
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
import sys
import os
import shutil
## Django modules
from django.core.management.base import BaseCommand, CommandError
## Third-party modules
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, ID, TEXT, STORED, KEYWORD
from whoosh.qparser import QueryParser
## NOC modules
from noc.main.models import fts_models


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Full-Text Search index"
    option_list=BaseCommand.option_list+(
        make_option(
            "--check", "-c",
            action="store_const",
            dest="action",
            const="check",
            help="Check index exists (returns 0 if OK, 1 otherwise)"
        ),
        make_option(
            "--create", "-C",
            action="store_const",
            dest="action",
            const="create",
            help="Create index"
        ),
        make_option(
            "--reindex", "-r",
            action="store_const",
            dest="action",
            const="reindex",
            help="Reindex database"
        ),

        make_option(
            "--query", "-q",
            action="store_const",
            dest="action",
            const="query",
            help="Query database"
        ),

        make_option(
            "--drop", "-d",
            action="store_const",
            dest="action",
            const="drop",
            help="Drop index database"
        )
    )

    INDEX = "local/index"

    def out(self, msg):
        if not self.verbose:
            return
        print msg

    def handle(self, *args, **options):
        self.verbose = bool(options.get("verbosity"))
        if "action" in options:
            if options["action"] == "check":
                self.handle_check()
            elif options["action"] == "create":
                self.handle_create()
            elif options["action"] == "reindex":
                self.handle_reindex()
            elif options["action"] == "query":
                self.handle_query(args)
            elif options["action"] == "drop":
                self.handle_drop()

    def check_index(self):
        return os.path.exists(self.INDEX)

    def create_index(self):
        self.out("Creating directory %s" % self.INDEX)
        os.mkdir(self.INDEX)
        schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),  # Title to show
            card=STORED,  # Object card
            content=TEXT,  # Searchable content
            tags=KEYWORD(stored=True, commas=True, scorable=True),
            url=STORED
        )
        self.out("Creating index directory")
        create_in(self.INDEX, schema)

    def handle_check(self):
        self.out("Checking FTS index in %s ..." % self.INDEX)
        if self.check_index():
            self.out("    ... exists")
            sys.exit(0)
        else:
            self.out("    ... not exists")
            sys.exit(1)

    def handle_create(self):
        # Check index is not exists
        self.out("Checking existing index in %s ..." % self.INDEX)
        if self.check_index():
            self.out("    ... Already exists")
            sys.exit(1)
        self.out("    ... Creating")
        # Create index
        self.create_index()
        self.out("Done")

    def reindex_model(self, writer, model):
        for o in model.objects.all():
            i = o.get_index()
            if not i.get("content") or not i.get("id") or not i.get("url"):
                continue
            fields = {
                "id": unicode(i["id"]),
                "title": unicode(i["title"]),
                "url": unicode(),
                "content": unicode(i["content"]),
                "card": unicode(i["card"]),
            }
            if i.get("tags"):
                fields["tags"] = u",".join(i["tags"])
            writer.update_document(**fields)

    def handle_reindex(self):
        self.out("Reindexing ...")
        if not self.check_index():
            self.create_index()
        index = open_dir(self.INDEX)
        for m in fts_models:
            self.out("    %s" % m)
            writer = index.writer()
            self.reindex_model(writer, fts_models[m])
            writer.commit()

    def handle_query(self, q):
        if not q:
            return
        index = open_dir(self.INDEX, readonly=True)
        parser = QueryParser("content", index.schema)
        query = parser.parse(q[0])
        with index.searcher() as searcher:
            result = searcher.search(query, limit=1000)
            for r in result:
                print "%s:" % r["title"]
                print "    %s" % r["card"]
                if r.get("tags"):
                    print "    Tags: %s" % r["tags"]
                print

    def handle_drop(self):
        self.out("Dropping index")
        if self.check_index():
            self.out("Removing %s" % self.INDEX)
            shutil.rmtree(self.INDEX)
