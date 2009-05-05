# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import MoinMoin wiki data to NOC KB
## USAGE:
## python manage.py convert-moin [--encoding=charset] [--language=lang] [--category=category] <path to moin data/ >
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction,reset_queries
from django.contrib.auth.models import User
from noc.main.models import Language,DatabaseStorage,database_storage
from noc.kb.models import KBEntry,KBEntryAttachment,KBCategory
from optparse import OptionParser, make_option
import os,re,stat,datetime,sys,types,gc

##
rx_hexseq=re.compile(r"\(((?:[0-9a-f][0-9a-f])+)\)")
##
## convert-moin command handler
##
class Command(BaseCommand):
    help="Import MoinMoin wiki into NOC KB"
    option_list=BaseCommand.option_list+(
        make_option("-e","--encoding",dest="encoding",default="utf-8"),
        make_option("-l","--language",dest="language",default="English"),
        make_option("-c","--category",dest="category")
    )
    def handle(self, *args, **options):
        self.encoding=options["encoding"]
        self.pages=os.path.join(args[0],"pages")
        transaction.enter_transaction_management()
        self.user=User.objects.order_by("id")[0] # Get first created user as owner
        self.language=Language.objects.get(name=options["language"])
        # Find category
        self.category=None
        if options["category"]:
            try:
                self.category=KBCategory.objects.get(name=options["category"])
            except KBCategory.DoesNotExist:
                self.category=KBCategory(name=options["category"])
                self.category.save()
        oc=len(gc.get_objects())
        for page in os.listdir(self.pages):
            self.convert_page(page)
            reset_queries()
            gc.collect()
            new_oc=len(gc.get_objects())
            self.out("%d leaked objects\n"%(new_oc-oc))
            oc=new_oc
        transaction.commit()
        transaction.leave_transaction_management()
    ##
    ## Progress output
    ##
    def out(self,s):
        if type(s)==types.UnicodeType:
            sys.stdout.write(s.encode("utf-8"))
        else:
            sys.stdout.write(unicode(s,self.encoding).encode("utf-8"))
        sys.stdout.flush()
    ##
    ## Convert single MoinMoin page
    ##
    def convert_page(self,page):
        # Convert (hex) sequences to unicode
        def convert_hexseq(m):
            seq=m.group(1)
            r=[]
            while seq:
                c=seq[:2]
                seq=seq[2:]
                r+=chr(int(c,16))
            r="".join(r)
            return unicode(r,self.encoding)
        root=os.path.join(self.pages,page)
        name=rx_hexseq.sub(convert_hexseq,page)
        self.out("Converting %s (%s)..."%(page,name))
        # Find current revisions
        current_path=os.path.join(root,"current")
        if not os.path.exists(current_path):
            return  # Return on incomplete pages
        with open(current_path) as f:
            current=f.read().split()
        # Write all revisions
        kbe=None
        revisions=sorted(os.listdir(os.path.join(root,"revisions")))
        for rev in revisions:
            rev_path=os.path.join(root,"revisions",rev)
            with open(rev_path) as f:
                body=self.convert_body(unicode(f.read(),self.encoding))
            mtime=datetime.datetime.fromtimestamp(os.stat(rev_path)[stat.ST_MTIME]) # Revision time
            if kbe is None:
                kbe=KBEntry(subject=name,body=body,language=self.language,markup_language="Creole")
                kbe.save(user=self.user,timestamp=mtime) # Revision history will be populated automatically
                if self.category:
                    kbe.categories.add(self.category)
            else:
                kbe.body=body
                kbe.save(user=self.user,timestamp=mtime) # Revision history will be populated automatically
        self.out("... %d revisions\n"%len(revisions))
        if kbe is None:
            return # Return when no revisions found
        # Write all attachments
        attachments_root=os.path.join(root,"attachments")
        if os.path.isdir(attachments_root):
            for a in os.listdir(attachments_root):
                self.out("     %s..."%a)
                a_path=os.path.join(attachments_root,a)
                mtime=datetime.datetime.fromtimestamp(os.stat(a_path)[stat.ST_MTIME]) # Attach modification time
                with open(a_path) as f:
                    dbs_path="/kb/%d/%s"%(kbe.id,a)
                    database_storage.save(dbs_path,f)
                    # Correct mtime
                    database_storage.set_mtime(dbs_path,mtime)
                KBEntryAttachment(kb_entry=kbe,name=a,file=dbs_path).save()
                self.out("...done\n")
    ##
    ## Convert MoinMoin syntax to Creole
    ##
    def convert_body(self,body):
        return body
