******************
Service Activation
******************
Overview
========

* Mediates with equipment.
* Provides generalized interface to perform commands on equipment and analyze results.
* Collects events from equpment from different sources (SNMP Trap, Syslog) performs filtration and stores for further processing

Terminology
============

* Managed Object - A piece of equipment or service, operated by Service Activation
* Profile - A representations of equipment class containing equipment capabilities and behavior specifics. (See SupportedEquipment for a list of profiles)
* Access scheme - Transport application protocol used to access equpment (Telnet, SSH, HTTP)
* SAE - Service Activation Engine. A hearth of **sa** module. Separated process responsible for dispatching tasks between activators and performing periodic tasks.
* Activator - Separate processes responsible for mediation with equipment.
* Network Domain - Logically, Physically or Administratively separated part of network. Examples: VRF, LAN behind NAT, city's part of network, etc. Direct communication between Network Domains is not necessary.

Architecture
============
Top level overview of **sa** architecture in a chart.

.. image:: sa_arch.png

Roles of the participants:

* SAE - dispatches tasks between activators, maintains common connectivity and initiates periodic tasks
* Activator - Connects to SAE on startup, passes authentication phase, accepts RPC messages from SAE, mediates with equipment using different ''access schemas'' (ssh, telnet, http, etc), collects SNMP Traps and syslog messages from Equipment and passes them to SAE
* Equipment - Managed Equipment. Equipment Specifics stored into ''profile''. Central profile repository stored at SAE and distributed to activators during self-update processes.

Strict separation between SAE and Activators has several benefits:

* Activators can be placed as close to equipment as possible:
* SAE and Activator uses bulk data exchange. All commands packed together to reduce delay impact and maximize throughoutput.  Though interactive protocols like telnet and ssh use short packets for communications all communications between SAE and Activator remains bulk. Data exchanged only when ready. Data chunks from several transactions are merged together into single packet when possible. Increased performance and stability on long links with high delay (think about sattelite), high packet loss (WiFi and Radio) or low bandwith (up to GPRS modem) immediately follow.
* SAE RPC protocol uses compression. All messages compressed before transmission which grealty reduce requirements to bandwidth and delays (Up to x4 on common equipment configuration fetching)
* SAE RPC protocol uses encryption (Work in progress) which greatly improve security even when using unenctypted protocols like telnet, http, snmp or syslog.
* Different activator can be maintained by different administrative departments, follow organizational structure, while remain centralized service
* Activator has low disk and memory footprint and can operate without writing to disk. Cheap controllers like Soekris Net series can be used as platform for Activator.
* Load offloaded from SAE to Activators. Scalability can be accepted by increasing number of activators.
* Activators can remain in physically or logically separated parts of network:
* SAE RPC interface uses TCP as transport. Connection initialized by Activator. So the protocol is transparent to NAT and firewalls. Activator could remain behind NAT still retaining operational state.
* Activator and SAE could be placed in different VRFs. Only one route per VRF must be leaked to maintain connectivity. This allows centralized management over several management VRFs. CPEs in MPLS L3VPN can be managed as well

SAE
===
Configuration
-------------
SAE configuration stored in etc/noc-sae.conf. Edit configuration file before starting SAE.

Running SAE
-----------
Daemon mode
^^^^^^^^^^^
By default SAE starts in daemon mode, detaches from terminal and continues execution in backgroung.
To run SAE::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py start

Foreground mode
^^^^^^^^^^^^^^^
When started in foreground mode SAE do not detaches from terminal and enforces full debug output directed to current terminal.
To run SAE in foreground mode::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py -f start

Stopping SAE
------------
To stop SAE run::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py stop


Activator
=========

Overview
--------
State Machine
^^^^^^^^^^^^^
From start up activator follows state machine:

.. image:: sa_activator_fsm.png

* Just after startup activator waits for 5 seconds, then tries to connect to SAE.
* When 10 second timeout expired or connection refused activator sleeps fo 10 seconds and retries connection
* On connection activator performs registration
* When started in stand-alone mode (see later) activator performs self-upgrade from SAE and restarts, when possible
* Then activator passes to ESTABLISHED state and ready to perform tasks

Registration
^^^^^^^^^^^^
Activator uses ''activator name'' and ''secret'' to authenticate. Digest authentication method used.
Activator should be created in database to pass authentication (See 'Creating Activator in Database' for details)

in-bundle and stand-alone mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Activator can be started from two modes:

* in-bundle - Activator started from common NOC distribution. No self-update necessary.
* stand-alone - Activator started from special lightweight stand-alone distribution with minimal dependencies.
 
stand-alone mode
^^^^^^^^^^^^^^^^

Stand-alone distribution is stripped NOC distribution with minimum files and dependencies.
Stand-alone distribution can be created from full NOC distribution by::

    $ cd /opt/noc
    $ ./scripts/clone-activator /tmp
    $ cd /tmp
    $ tar cf - noc | gzip > noc-activator.tgz

Distribute and unpack noc-activator.tgz to target host.

Activator performs self-upgrade on startup when launched in stand-alone mode, so it must have write permissions to own directory (including etc/noc-activator.defaults one)

Running Activator
-----------------

Daemon mode
^^^^^^^^^^^

By default activator starts in daemon mode, detaches from terminal and continues execution in backgroung.
To run SAE::

    $ cd /opt/noc
    $ ./scripts/noc-activator.py start

Foreground mode
^^^^^^^^^^^^^^^

When started in foreground mode activator do not detaches from terminal and enforces full debug output directed to current terminal.
To run SAE in foreground mode::

    $ cd /opt/noc
    $ ./scripts/noc-activator.py -f start


Stopping Activator
------------------

To stop Activator run::

    $ cd /opt/noc
    $ ./scripts/noc-activator.py stop


Enabling collectors
-------------------

Syslog
^^^^^^
To enable syslog collector set ''listen_syslog'' variable in [activator] section of etc/noc-activator.conf to IP address or name of interface of syslog collector

SNMP Traps
^^^^^^^^^^

To enable SNMP Trap collector set ''listen_traps'' variable in [activator] section of etc/noc-activator.conf to IP address or name of interface of SNMP trap collector

Managed objects
===============

Periodic Tasks
==============
SAE supports concept of periodic tasks. Periodic tasks are code snippets repeatedly executed every given interval of time.
Periodic tasks are similar to UNIX traditional ''cron'' though some differences are present:

* periodic tasks executed in context of SAE process in separate threads
* periodic tasks share common database connection pool
* periodic tasks are python modules residing in ''periodics'' directory of the NOC modules
* periodic tasks are the part of NOC modules itself
* periodic tasks have access to SAE internals

Map/Reduce Scripts
==================
Map/Reduce scripts is a way of parallel execution of scripts on large number of equipment with final validation
and processing of the result.

Map/Reduce scripts are combined from the three entries: Object Selectors, Map Scripts and Reduce Scripts

Object Selectors
----------------
Object selectors are like preserved queries returning a list of managed objects. Object selector can filter managed objects using
given criteria. Object selectors can use result of other selectors, allowing to combine them together to reach any required granularity.

The task of the object selector is to determine on which managed objects to execute Map Scripts.

For example:

* All objects
* All Cisco IOS-based
* All Cisco MPLS PE
* All access switches
* Access switches in Area A
* Access switches in Area B
* Access switches in areas A and B

Map Scripts
-----------
Map Scripts are the common Service Activation scripts which are executed in parallel on all managed objects determined by selector.
The results of Map Scripts are returned to the Reduce Script. Some Map Scripts can fail, Some may not be executed at all. This is
normal situation. This is a task of Reduce script to process failure condition properly.

Reduce Scripts
--------------
Reduce Scripts are to process the results of all Map Scripts at once. The common result of Reduce Script is an report, though
it is possible even to start a new Map/Reduce task.

Examples
--------

Version inventory
^^^^^^^^^^^^^^^^^
Selector: all objects, reduce script: MatrixReport, map script: get_version

Parallel command execution
^^^^^^^^^^^^^^^^^^^^^^^^^^
Selector: all Cisco 7600, reduce script: ResultReport, map script: commands,
map script parameters: {"commands":["show version","show module"]}

SAE Protocol
============
SAE use lightweight RPC protocol to communicate. Protocol has following distinctive features:
  
* `Google's Protocol Buffers <http://code.google.com/p/protobuf/>`_ used for message serialization and as RPC interface skeleton
* gzip message compression used to reduce bandwidth
* SSL encryption [Work in progress]

Complete RPC message definition stored in sa/protocols/sae.proto

Debugging
=========
In case when SAE or activator behave improperly (Stall, Became memory or CPU hog)
send SIGUSR2 signal to the process. Daemon will write current stack frame to the log file.

Please use traceback provided aside with description of symptoms to fill in [/newticket Bug Request]

Forms
=====
Managed Objects
---------------
Permissions
^^^^^^^^^^^
======= ========================================
add     sa | Managed Object | Can add Managed Object
change  sa | Managed Object | Can change Managed Object
delete  sa | Managed Object | Can delete Managed Object
======= ========================================

Task Schedules
--------------
Permissions
^^^^^^^^^^^
======= ========================================
add     sa | task schedule | Can add task schedule
change  sa | task schedule | Can change task schedule
delete  sa | task schedule | Can delete task schedule
======= ========================================

Activators
----------
* **Name** - Activator name. Used for authentication. Must match with [activator]/name in noc-activator.conf
* **IP** - Source IP address seen by SAE. May be one of activator's interfaces or NAT pool if on the way. SAE forcefully refuses connection from unknown addresses.
* **Auth string** - Secret used for authentication. Must match with [activator]/secret in noc-activator.conf
* **Is Active** - Can activator authenticate now. Set checkbox when activator can authenticate, or uncheck to temporary disable following authentication attempts. Changing **Is Active** does not follow immediately activator connect/disconnect.

Permissions
^^^^^^^^^^^
======= ========================================
add     sa | Activator | Can add Activator
change  sa | Activator | Can change Activator
delete  sa | Activator | Can delete Activator
======= ========================================

Administrative Domains
----------------------
Permissions
^^^^^^^^^^^
======= ========================================
add     sa | Administrative Domain | Can add Administrative Domain
change  sa | Administrative Domain | Can change Administrative Domain
delete  sa | Administrative Domain | Can delete Administrative Domain
======= ========================================

Object Groups
-------------
Permissions
^^^^^^^^^^^
======= ========================================
add     sa | Object Group | Can add Object Group
change  sa | Object Group | Can change Object Group
delete  sa | Object Group | Can delete Object Group
======= ========================================

User Access
-----------
Permissions
^^^^^^^^^^^
======= ========================================
add     sa | User Access | Can add User Access
change  sa | User Access | Can change User Access
delete  sa | User Access | Can delete User Access
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Reports
=======
Configs by Groups
-----------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Objects by Profile and Domains
------------------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Scripts
-------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Objects by Administrative Domains
---------------------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Supported Equipment
-------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Objects by Profiles
-------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

