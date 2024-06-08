# Discovery

Statical inventory databases are doomed to be out-of-dated. Small changes
which goes undocumented, emergency equipment replacing, staff overloading
by other important tasks, all leads to increasing the gap between
database and actual state. So the properly built infrastructure
must be capable of discovering of actual state and fixing the differences.

So discovery process is the heart of NOC. Its primary target is not just
fixing the differences, but to collect and update a deep knowledge
of what is really going on network.

Discovery process performs a lot of tasks:

* Detects replacements to other platform
* Suggest a proper access credentials
* Detects firmware information
* Detects configured capabilities
* Detects hardware configuration, including chassis, modules and transcevers
* Collects and keeps full story of configuration
* Performs configuration policy checks
* Collects physical interfaces settings and operative statuses
* Collects logical interfaces settings
* Collects MAC addresses database
* Discovers network topology using various network protocols: LLDP, STP,
  FDP, NDP, LACP, UDLD, BFD and other. NOC is ever capable to restore topology
  using only MAC database state
* Tracks IP addresses usage
* Tracks VLAN usage
* Tracks phone number usages
* Collects metrics

Discovery process maintains separate schedules for each managed object.
Tasks are evenly separated upon the time, eliminating high spikes
of network management traffic.

## See Also

* [Discovery Reference](../discovery-reference/index.md)