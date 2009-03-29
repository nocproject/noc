************
Updating NOC
************

Updating
========

Updating from Mercurial repo
----------------------------
Fetch updates::
    
    # cd /opt/noc
    # hg pull -u
    
Updating from source
--------------------
Fetch and unpack new version::

    # wget http://......
    # gzip -dc noc-<version> | tar xf -
    # cd noc-<version>
    # python setup.py install

Syncronize database
===================
Syncronize database, fault management rules and MIBs and documentation after software update::

    # su - noc
    $ cd /opt/noc/
    $ ./scripts/post-update

