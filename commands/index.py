# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Full-Text search manipulation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.core.management.base import BaseCommand
from noc.main.models.textindex import TextIndex
from models import FTS_MODELS, get_model


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            action="store",
            dest="config",
            default=os.environ.get("NOC_CONFIG", "etc/noc.yml"),
            help="Configuration path"
        )
        subparsers = parser.add_subparsers(
            dest="cmd",
            help="sub-commands help"
        )
        # Search parameters
        search_parser = subparsers.add_parser(
            "search",
            help="Full-text search"
        )
        search_parser.add_argument(
            "query",
            nargs=1,
            help="Query terms"
        )
        search_parser.add_argument(
            "--format",
            action="store",
            dest="format",
            default="yaml",
            choices=["yaml", "json"],
            help="Output format"
        )
        # Rebuild parameters
        rebuild_parser = subparsers.add_parser(
            "rebuild",
            help="Rebuild index"
        )

    def handle(self, cmd, *args, **options):
        getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_search(self, query, format, *args, **options):
        r = []
        for qr in TextIndex.search(query[0]):
            r += [{
                "id": str("%s:%s" % (qr.model, qr.object)),
                "title": str(qr.title),
                "card": str(qr.card)
            }]
            if qr.tags:
                r[-1]["tags"] = [str(x) for x in qr.tags]
        if format == "yaml":
            import yaml
            yaml.dump(r, stream=self.stdout)
        else:
            import json
            json.dump(r, self.stdout)

    def handle_rebuild(self, *args, **options):
        for model_id in FTS_MODELS:
            self.stdout.write("Indexing %s: " % model_id)
            model = get_model(model_id)
            n = 0
            for o in model.objects.all():
                TextIndex.update_index(model, o)
                n += 1
            self.stdout.write("%d records indexed\n" % n)


if __name__ == "__main__":
    Command().run()
