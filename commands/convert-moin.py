# ---------------------------------------------------------------------
# Import MoinMoin wiki data to NOC KB
# USAGE:
# python manage.py convert-moin [--encoding=charset] [--language=lang] [--tags=<taglist>] <path to moin data/ >
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import os
import re
import stat
import datetime
import sys
import gc

# NOC modules
from noc.aaa.models.user import User
from noc.core.management.base import BaseCommand
from noc.main.models.language import Language
from noc.main.models.databasestorage import database_storage
from noc.kb.models.kbentry import KBEntry
from noc.kb.models.kbentryattachment import KBEntryAttachment
from noc.core.comp import smart_text, smart_bytes

#
rx_hexseq = re.compile(r"\(((?:[0-9a-f][0-9a-f])+)\)")


class Command(BaseCommand):
    help = "Import MoinMoin wiki into NOC KB"

    def add_arguments(self, parser):
        (
            parser.add_argument(
                "-e", "--encoding", dest="encoding", default="utf-8", help="Encoding"
            ),
        )
        (
            parser.add_argument(
                "-l", "--language", dest="language", default="English", help="Wiki Language"
            ),
        )
        (parser.add_argument("-t", "--tags", dest="tags", help="Tags"),)
        parser.add_argument("args", nargs=argparse.REMAINDER, help="List of convert pages")

    def handle(self, *args, **options):
        self.encoding = options["encoding"]
        self.pages = os.path.join(args[0], "pages")
        self.user = User.objects.order_by("id")[0]  # Get first created user as owner
        self.language = Language.objects.get(name=options["language"])
        # Find category
        self.tags = options["tags"]
        oc = len(gc.get_objects())
        for page in os.listdir(self.pages):
            self.convert_page(page)
            gc.collect()
            new_oc = len(gc.get_objects())
            self.out("%d leaked objects\n" % (new_oc - oc))
            oc = new_oc

    #
    # Progress output
    #

    def out(self, s):
        if isinstance(s, str):
            sys.stdout.write(s.encode("utf-8"))
        else:
            sys.stdout.write(smart_bytes(smart_text(s, encoding=self.encoding)))
        sys.stdout.flush()

    #
    # Convert single MoinMoin page
    #

    def convert_page(self, page):
        # Convert (hex) sequences to unicode
        def convert_hexseq(m):
            seq = m.group(1)
            r = []
            while seq:
                c = seq[:2]
                seq = seq[2:]
                r += chr(int(c, 16))
            r = "".join(r)
            return smart_text(r, encoding=self.encoding)

        root = os.path.join(self.pages, page)
        name = rx_hexseq.sub(convert_hexseq, page)
        self.out("Converting %s (%s)..." % (page, name))
        # Find current revisions
        current_path = os.path.join(root, "current")
        if not os.path.exists(current_path):
            return  # Return on incomplete pages
        with open(current_path) as f:
            current = f.read().split()  # noqa
        # Write all revisions
        kbe = None
        revisions = sorted(os.listdir(os.path.join(root, "revisions")))
        for rev in revisions:
            rev_path = os.path.join(root, "revisions", rev)
            with open(rev_path) as f:
                body = self.convert_body(smart_text(f.read(), encoding=self.encoding))
            mtime = datetime.datetime.fromtimestamp(
                os.stat(rev_path)[stat.ST_MTIME]
            )  # Revision time
            if kbe is None:
                kbe = KBEntry(
                    subject=name, body=body, language=self.language, markup_language="Creole"
                )
                kbe.save(
                    user=self.user, timestamp=mtime
                )  # Revision history will be populated automatically
                if self.tags:
                    kbe.tags = self.tags
                    kbe.save(user=self.user, timestamp=mtime)
            else:
                kbe.body = body
                kbe.save(
                    user=self.user, timestamp=mtime
                )  # Revision history will be populated automatically
        self.out("... %d revisions\n" % len(revisions))
        if kbe is None:
            return  # Return when no revisions found
        # Write all attachments
        attachments_root = os.path.join(root, "attachments")
        if os.path.isdir(attachments_root):
            for a in os.listdir(attachments_root):
                self.out("     %s..." % a)
                a_path = os.path.join(attachments_root, a)
                mtime = datetime.datetime.fromtimestamp(
                    os.stat(a_path)[stat.ST_MTIME]
                )  # Attach modification time
                with open(a_path) as f:
                    dbs_path = "/kb/%d/%s" % (kbe.id, a)
                    database_storage.save(dbs_path, f)
                    # Correct mtime
                    database_storage.set_mtime(dbs_path, mtime)
                KBEntryAttachment(kb_entry=kbe, name=a, file=dbs_path).save()
                self.out("...done\n")

    #
    # Convert MoinMoin syntax to Creole
    #

    def convert_body(self, body):
        return body


if __name__ == "__main__":
    Command().run()
