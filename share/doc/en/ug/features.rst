********
Features
********

Flexibility and Portability
===========================

* NOC mostly implemented in python language and available on all major telco platforms: Solaris, FreeBSD, Linux, Mac OS X

Security
========

* Privilege separation for all major components for collaborative use
* Record-level permissions

Web Interface
=============

* Neat Django-based web interface
* All major operation and configuration can be performed via web interface

Service Activation
==================

* Interacts with wide range of equipment
* Flexible framework to quickly create additional equipment support (Sometime less then 2 minutes)
* Service activation script framework
* Collect SNMP traps and syslog messages from objects
* Multiple activator support
* Activators can reside in different overlapping address spaces
* Activators can work from behind NAT

Fault Management
================

* Uses Service Activation subsystem
* Collects events from managed objects (SNMP Trap, Syslog)
* Performs event classification, correlation and root-cause analysis (Experimental)

Configuration Management
========================

* Uses Service Activation subsystem
* Grabs configuration from wide range of equipment
* Configuration stored on version control
* Any revision of configuration accessible via web interface
* Flexible notification on configuration changes
* Forced re-read of configuration on specific SNMP traps or syslog messages
* Pluggable VCS interface (Mercurial, CVS, etc)

Virtual Circuit Management
==========================

* Database of VC identifiers and tags
* 802.1Q VLANs, 802.1ad Q-in-Q VLAN stacks, FrameRelay DLCIs, MPLS label stacks, ATM VPI/VCIs, X.25 logical groups/logical channels are supported
* Direct import of existing VLANs from equipment

Address Space Management
========================

* Multi-VRF address space management
* Nested address block allocations
* Used ip address database
* Address space usage reports
* Allocated and free blocks reports
* Direct import of IP addresses via DNS zone transfer or from CSV file

Peering Management
==================

* Database of BGP peers
* Database of ASes and AS-SETs
* RPSL generator
* Prefix list generator

DNS Management
==============

* Forward and Reverse zone generator
* Pluggable zone generator interface (BINDv9 supported)
* Web interface for zone creating and modification
* Address Space Management integration
* Zone and config file provisioning
* Web interface to distribute load between nameservers

Reporting
=========

* Flexible reporting
