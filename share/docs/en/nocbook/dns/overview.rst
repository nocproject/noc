***
DNS
***
Overview
========
The DNS module is responsible for generating, maintaining and provisioning DNS zones.
DNS module workflow represented on chart:

.. image:: dns_workflow.png

Zones are built automatically from ip address database (*ip* and *fqdn* fields of IPv4 Address) with
addition of manual given entries from "DNS Zone Records". Zones are built during "pull" process
by *cm.dns_pull* periodic task. Zones are stored in Configuration Management's repo and accessible
via CM tools provided. Zones are distributed to the nameservers during the "push" process performed
by *cm.dns_push* periodic task.

NOC has pluggable nameserver support, allowing single zone to be served by different types of
nameservers (i.e. BIND and PowerDNS). NOC offers flexible way to integrate with third-party
DNS provisioning tools. Provided provisioning tools can be used as well as your own.

Terminology
===========

* Zone - DNS zone (forward and reverse)
* DNS Server - name server process
* Generator - plugin performing zone file generation for specific DNS Server type
* Zone profile - shared common information about zones, include SOA record and distribution list
* Provisioning - a process of bringing updated zone online

Generation and distribution process
===================================
First you must define your DNS server (DNS > Setup > DNS Server). You must define name, type (Generator) and
ip address of DNS server. Fill "Provisioning" field with a command to perform zone provisioning (See below).
Create at least one DNS Server.

Next step is to create Zone Profile (DNS > Setup > Zone Profiles). Zone Profile is a shared common information
including SOA, contact, refresh, TTL and other parameters and a list of master and slave nameservers. Create
at least one Zone Profile.

Then you can create zones (DNS > Zones). Set up domain name. Reverse zone for X.Y.Z.0/24 block must be
created as Z.Y.X.in-addr.arpa zone. Select Zone Profile. Mark "Auto Generated?" checkbox if you wish zone
to be automatically generated and distributed. "Serial" field will be generated automatically so usually
you have no need to change it manually. Additional zone records can be set up from Zones form. You can
add MX, CNAME and other information not present in IP database.

Last step is to enable cm.dns_pull and cm.dns_push periodic tasks (Service Activation > Task Schedules). 300 seconds
interval is sufficient for common needs.

Zones will be build from:
* Manually set records
* *A* records (fqdn A ip) from Address Space Management database for forward zones
* *PTR* records (ip PTR fqdn) from Address Space Management database for reverse zones

During the *push* process *Provisioning* field for each DNS server will be taken, built-in variables
will be expanded and result will be performed as shell command.

Variables to expand:

============ ==========================
%(ns)s       DNS Server name
%(ip)s       DNS Server IP address
%(repo)s     Root of DNS repo
%(rsync)s    Path to the rsync
%(vsc_path)s Path to the VCS tool
============ ==========================

Commands will be executed from *noc* system user. Current directory will be set to the DNS repo root.
See DNS Server Setup for *Provisioning* value recomendation

DNS Server Setup
================
BIND
----
Create SSH key for user *noc* on server hosting SAE::

    noc$ ssh-keygen -t dsa
    
Create user *noc* on DNS server. Copy ~noc/.ssh/id_dsa.pub key from SAE
and place it as ~noc/.ssh/authorized_keys

Create *autozones* directory in your named chroot jail. *autozones* directory must be
owned by user *noc*. Create *autozones/slave* directory, owned by your *named* user.

Append to the end of your *named.conf*::

    include "autozones/<your dns server name>/autozones.conf";

Initialize mercurial repo in *autozones*::

    noc$ cd autozones
    noc$ hg init

Copy hgrc, named-update and named-update.conf from *share/dns/bind* directory of NOC distribution
and place them in *autozones/.hg/* directory. Edit hgrc and change *changegroup* variable to <full sudo path> <full named-update path>.
Edit named-update.conf according your system path. Ensure named-update is executable by root.

Append following line to your *sudoers* file::

    noc     ALL = NOPASSWD: <full path to your named-update>

Finally open web interface and set DNS Server *Provisioning* field to::

    %(vcs_path)s push --remotecmd <remote-hg-path> ssh://noc@%(ip)s//var/named/autozones/

Where <remote-hg-path> is a path to *hg* on DNS Server. Note double slash after ip.
Set DNS Server *Autozones Path* field to::

    autozones/%(ns)s/

Installation complete. All changes will be pushed from NOC repository to DNS server's repository.
*named-update* will be started on every change. *named-update* checks resulting config and
zones. In case of success *named-update* executes command set as *NAMED_RELOAD* in *named-update.conf* (pkill/killall -HUP usually)
and forces named to reload zones. In case of failure autozones directory will be reverted to the previous working version.

Forms
=====
Zones
-----
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | DNS Zone | Can add DNS Zone
change  dns | DNS Zone | Can change DNS Zone
delete  dns | DNS Zone | Can delete DNS Zone
======= ========================================

Setup
=====
DNS Servers
-----------
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | DNS Server | Can add DNS Server
change  dns | DNS Server | Can change DNS Server
delete  dns | DNS Server | Can delete DNS Server
======= ========================================

Zone Profiles
-------------
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | dns zone profile | Can add dns zone profile
change  dns | dns zone profile | Can change dns zone profile
delete  dns | dns zone profile | Can delete dns zone profile
======= ========================================

Zone Record Types
-----------------
Permissions
^^^^^^^^^^^
======= ========================================
add     dns | DNS Zone Record Type | Can add DNS Zone Record Type
change  dns | DNS Zone Record Type | Can change DNS Zone Record Type
delete  dns | DNS Zone Record Type | Can delete DNS Zone Record Type
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

