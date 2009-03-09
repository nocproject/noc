************
Updating NOC
************

Updating from Mercurial repo
============================
Fetch updates::
    
    # cd /opt/noc
    # hg pull -u
    
Syncronize database, fault management rules and MIBs and documentation::

    # ./scripts/post-update

Updating from source
====================
Fetch and unpack new version::

    # wget http://......
    # gzip -dc noc-<version> | tar xf -
    # cd noc-<version>
    # python manage.py install

Syncronize database, fault management rules and MIBs and documentation::

    # cd /opt/noc/
    # ./scripts/post-update

