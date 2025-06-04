# ----------------------------------------------------------------------
# ./noc confdb
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import os

# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config
from noc.core.mongo.connection import connect
from noc.core.profile.loader import loader
from noc.core.text import format_table
from noc.core.comp import smart_text


class Command(BaseCommand):
    PREFIX = config.path.cp_new

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # syntax command
        syntax_parser = subparsers.add_parser("syntax")
        syntax_parser.add_argument("--profile", help="Profile Name")
        syntax_parser.add_argument("path", nargs=argparse.REMAINDER)
        # tokenizer command
        tokenizer_parser = subparsers.add_parser("tokenizer")
        tokenizer_parser.add_argument("--object", type=smart_text, help="Managed Object ID")
        tokenizer_parser.add_argument("--profile", help="Profile Name")
        tokenizer_parser.add_argument("--config", help="Config Path")
        # config command
        normalizer_parser = subparsers.add_parser("normalizer")
        normalizer_parser.add_argument("--object", type=smart_text, help="Managed Object ID")
        normalizer_parser.add_argument("--profile", help="Profile Name")
        normalizer_parser.add_argument("--config", help="Config Path")
        normalizer_parser.add_argument("--errors-policy", help="Errors Policy")
        # query command
        query_parser = subparsers.add_parser("query")
        query_parser.add_argument("--object", type=smart_text, help="Managed Object ID")
        query_parser.add_argument("--profile", help="Profile Name")
        query_parser.add_argument("--config", help="Config Path")
        query_parser.add_argument("query", help="Query request")
        # query command
        dump_parser = subparsers.add_parser("dump")
        dump_parser.add_argument(
            "--show-hints", action="store_true", help="Disable cleanup hints section"
        )
        dump_parser.add_argument("--object", type=smart_text, help="Managed Object ID")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_syntax(self, path=None, profile=None, *args, **kwargs):
        def dump_node(node, level=0, recursive=True):
            indent = "  " * level
            if node.name:
                label = "<%s>" % node.name
            elif node.token is None:
                label = "ANY"
            else:
                label = node.token
            if node.multi:
                label = "*%s" % label
            self.print("%s%s" % (indent, label))
            if recursive and node.children:
                for nc in node.children:
                    dump_node(nc, level + 1)

        def find_root(children, rest_path, level=0):
            if not rest_path:
                return children
            if len(children) == 1 and not children[0].token:
                dump_node(children[0], level, recursive=False)
                return find_root(children[0].children, rest_path[1:], level=level + 1)
            p = rest_path[0]
            for cc in children:
                if cc.token == p:
                    dump_node(cc, level, recursive=False)
                    return find_root(cc.children, rest_path[1:], level=level + 1)

        from noc.core.confdb.syntax.base import SYNTAX
        from noc.core.handler import get_handler

        s = SYNTAX
        if profile:
            p = loader.get_profile(profile)
            if not p:
                self.die("Invalid profile: %s" % profile)
            n_handler, n_config = p.get_config_normalizer(self)
            n_cls = get_handler("noc.sa.profiles.%s.confdb.normalizer.%s" % (p.name, n_handler))
            s = n_cls.SYNTAX
        root = find_root(s, path)
        if not root:
            return
        for c in root:
            dump_node(c, level=len(path) if path else 0)

    def handle_tokenizer(self, object=None, profile=None, config=None, *args, **kwargs):
        cfg = None
        if config:
            if not os.path.exists(config):
                self.die("File not found: %s" % config)
            with open(config) as f:
                cfg = f.read()
        if object:
            connect()
            from noc.sa.models.managedobject import ManagedObject

            mo = ManagedObject.objects.get(name=object)
            if not mo:
                self.die("Managed Object not found")
        elif profile:
            p = loader.get_profile(profile)
            if not p:
                self.die("Invalid profile: %s" % profile)
            if not cfg:
                self.die("Specify config file with --config option")
            # Mock up tokenizer
            connect()
            from noc.sa.models.managedobject import ManagedObject

            mo = ManagedObject.mock_object(profile=profile)
        else:
            self.die("Eigther object or profile must be set")
        tokenizer = mo.iter_config_tokens(config=cfg)
        for token in tokenizer:
            self.print(token)

    def handle_normalizer(
        self, object=None, profile=None, config=None, errors_policy=None, *args, **kwargs
    ):
        cfg = None
        if config:
            if not os.path.exists(config):
                self.die("File not found: %s" % config)
            with open(config) as f:
                cfg = f.read()
        if object:
            from noc.sa.models.managedobject import ManagedObject

            connect()
            mo = ManagedObject.objects.get(name=object)
            if not mo:
                self.die("Managed Object not found")
        elif profile:
            p = loader.get_profile(profile)
            if not p:
                self.die("Invalid profile: %s" % profile)
            if not cfg:
                self.die("Specify config file with --config option")
            # Mock up tokenizer
            connect()
            from noc.sa.models.managedobject import ManagedObject

            mo = ManagedObject.mock_object(profile=profile)
        else:
            self.die("Eigther object or profile must be set")
        normalizer = mo.iter_normalized_tokens(config=cfg, errors_policy=errors_policy)
        try:
            for token in normalizer:
                self.print(token)
        except StopIteration as e:
            self.print(f"Stop processing when error: {e}")

    def handle_query(self, object=None, profile=None, config=None, query=None, *args, **kwargs):
        cfg = None
        if config:
            if not os.path.exists(config):
                self.die("File not found: %s" % config)
            with open(config) as f:
                cfg = f.read()
        if object:
            connect()
            from noc.sa.models.managedobject import ManagedObject

            mo = ManagedObject.objects.get(name=object)
            if not mo:
                self.die("Managed Object not found")
        elif profile:
            p = loader.get_profile(profile)
            if not p:
                self.die("Invalid profile: %s" % profile)
            if not cfg:
                self.die("Specify config file with --config option")
            # Mock up tokenizer
            connect()
            from noc.sa.models.managedobject import ManagedObject

            mo = ManagedObject.mock_object(profile=profile)
        else:
            self.die("Eigther object or profile must be set")
        confdb = mo.get_confdb()
        headers = []
        table = []
        width = []
        for r in confdb.query(query):
            row = []
            for key in r:
                if key not in headers:
                    headers += [key]
                    width += [40]
                row.insert(headers.index(key), r[key])
            table += [row]
        if table:
            self.print("Result:\n", format_table(width, [headers] + table))
        else:
            self.print("Result:")

    def handle_dump(self, object=None, show_hints=False, *args, **kwargs):
        if object:
            connect()
            from noc.sa.models.managedobject import ManagedObject

            mo = ManagedObject.objects.get(name=object)
            if not mo:
                self.die("Managed Object not found")
        confdb = mo.get_confdb(cleanup=not show_hints)
        self.print(confdb.dump())


if __name__ == "__main__":
    Command().run()
