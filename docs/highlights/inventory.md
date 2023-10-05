# Inventory

It is our strong belief that monitoring without underlying inventory
is profanation. You must know what you have then you can check it working
properly. The centralized database of your assets usually referred
as *Network Resource Inventory* (NRI) or simple *Inventory*.

NOC focuses you on keeping your inventory clean and up-to-date and define monitoring
policies. Policies are group configuration that applied automatically
when all prerequisites satisfied. So, by keeping inventory you'll get
monitoring as a bonus.

NOC keep both Physical and Logical inventories.

Physical inventory contains:

* Points of Presents (PoP) with geographic coordinates.
* Floors, rooms, racks.
* Cable infrastructure (Manholes and conduits).
* Chassis, line cards, transceivers.
* Physical interfaces.

Logical inventory contains:

* Managed Objects.
* Logical interfaces (SubInterfaces).
* L2 Links.
* Network Segments.
* Projects.
* Suppliers.
* Subscribers and Services.
* VPNs, IP Prefixes, IP Addresses (IPAM).
* VLANs.
* Dialplans, Phone Ranges and Phone Numbers.
* SLA probe sessions.
* Autonomous Systems (AS) and BGP peers.
* MAC addresses.

NOC populates most of inventory data for you via [Discovery Process](../discovery-reference/index.md).

## See Also

* [Topology Processing Features](../topology-processing-features/index.md)
* [Discovery Reference](../discovery-reference/index.md)