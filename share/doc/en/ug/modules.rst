************
NOC Modules
************

NOC functionality is separated into modules. Depending on your task two or more modules can be used.

main
====
Core of the NOC. Contains libraries, frameworks, initialization code, documentation and reporting engine.

sa
==
Service activation. Mediates with equipment. Provides generalized interface to perform commands
on equipment and analyze results. SA module allows system to interact with network equipment directly
to perform maintenance, diagnostic, troubleshooting and configuration tasks.

fm
==
Fault Management. Deals with events. Events are result of network activity,
user operations, clients activity, equipment faults etc. Working network can generate
thousands of events every minute. FM module allows to collect them, classify, assign priorities,
correlate events and automatically determine root cause of failure. System supports life cycle
of events ensuring no important events left unnoticed or unhandled.

pm
==
Performance Management. Polls network equipment and collect various performance data. Collected
data are checked against defined thresholds and stored into database for further analytic processing.
PM module generates FM events in case of probe failure or out-of-the-thresholds data.

cm
==
Configuration management. Contains generalized interface to Version Control System
to track the state and changes of the configuration objects. Web interface allows to preview given object
for an any moment of time and to preview differences between any two moments of time.
System performs automatically notification when configuration object has been changed.

Objects handled by cm:

* Device configurations
* DNS zones
* RPSL objects
* Prefix lists

cm performs two major operation: ''push'' to repository and ''pull'' from repository

vc
==
Virtual circuits management. Simple database of allocated VC identifiers of different types.
VCs are separated into VC Domains while remain unique within VC Domain and own kind.

Supported VC Types:

* 802.1Q VLAN
* 802.1ad Q-in-Q VLAN stack
* FrameRelay DLCI
* MPLS label stack (up to 2 labels)
* ATM VPI/VCI
* X.25 logical groups/logical channel

System can automatically import existing VLANs from equipment.

peer
====
Peering management. Contains database of major peering objects:

* Maintainers
* Persons
* Autonomous systems
* AS-Sets
* BGP peers 
* Communities

Generates valid RPSL representation for database objects.
Generates optimized BGP filters. Provides integrated looking glass for debugging purposes.
RPSL representation and prefix-lists are stored in cm repo to track changes.

ip
==
IP Address Management. Manages allocation and suballocations for peer module AS objects.
suballocations can be nested to any required level. Supports multi-VRF address space management.
Contains database of allocated prefixes and IP addresses. Controls address space allocation and usage.

dns
===
DNS Provisioning. Generates forward and reverse zones for allocated IP addresses (ip module). Contains web-interface
for DNS Zone editing and provisioning. Generated DNS Zones are stored in cm repo.
Resulting zones and configuration are provisioned to the DNS Servers.
Zones can be redistributed via several authoritative DNS servers (may be of different types) allowing to balance the load.

kb
==
Knowledge Base. Database to share knowledge between the staff. Knowledge represented as a set of the articles.
Article is a free-form text message (possible) containing some pieces of knowledge to be shared:
troubleshooting info, hints, references, rumors, FAQs, whitepapers, guides, manuals,
spoilers, common cases and other info. KB supports pluggable article syntax from plain-text and CSV to wiki-like Creole
allowing easy customization to specific workflow.