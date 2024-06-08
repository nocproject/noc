# Interface

Initially, NOC is the management of network infrastructure, and an important part of the network is interfaces (`Interfaces`). The main features of working with interfaces:

* The interface is a **Resource** (`Resource`).
* Interfaces appear in the system during the discovery process (`Discovery`). Interface discovery occurs as part of the [`Interface Discovery`](../../discovery-reference/box/interface.md) polling.
* Links (`Link`) are established between interfaces.
* Group settings [`Interface Profile`](../interface-profile/index.md) can be applied to the interface:
    * You can configure the set of collected metrics.
    * Configure FM event handling.
    * Validate configuration.
* The interface can be associated with:
    * Project [Project]()
    * Service [Service](../service/index.md)
    * `L2 Domain` [VC Domain]()
* Assignment of resource groups (`Resource Group`) is supported.

## Managing Interfaces

Interfaces are located in the menu `Service Activation -> Managed Objects (ManagedObjects) -> <Object> -> Interfaces (Interfaces)`

![](interfaces-mo-physical-form.png)

Several tabs are available on the form:

* Physical - displays interfaces with the type `Physical`.
* LAG - aggregating interfaces.
* (`Switchport`) - sub-interfaces with `AFI` - `BRIDGE`.
* L3 - sub-interfaces with `AFI` - `IPv4` or `IPv6`.

### Group Settings

Group settings for Interfaces (`Interfaces`) are concentrated in interface profiles [Interface Profile](../interface-profile/index.md).

## Interface Classification

<!-- prettier-ignore -->
!!! info

  In version 21.1, the mechanism for classifying interfaces is replaced by the mechanism of automatic profile assignment [Dynamic Classification Policy](../dynamic-profile-classification/index.md).

At some point, there are many interfaces, and manual profile assignment can be tedious. To automate the profile assignment process, there are rules for classifying interfaces. They allow you to assign an interface profile based on multiple criteria. The rules are executed during interface discovery.

Classification rules for interfaces are located in the menu `Inventory -> Setup -> Interface Classification Rules`

![](iface_classification_rule_exmpl1.png)

Inside, the rule consists of:

* **Active** - the status of the rule (Active/Disabled).
* **Priority** - the rule's order number in the chain.
* **Selector** - the selector that determines which objects fall under the rule (used for grouping ManagedObjects by some characteristic/characteristics. Located in `Service Activation -> Setup -> Selectors`).
* **Interface Profile** [Interface profile](../interface-profile/index.md) - the interface profile assigned when the rule matches.
* List of criteria (`Match rule`) - conditions under which the rule matches. The rule operates with the **AND** operation, meaning all listed conditions must match for the rule to trigger.

<!-- prettier-ignore -->
!!! info 
  Be careful when filling out the `Match rule` table. Do not leave empty rows; this may lead to incorrect discovery.

### Operating Principles

* Rules are grouped into **chains** in ascending order of the **Order** field.
* Rules are executed in ascending order (starting from 0), and execution stops at the ***first match***.
* There are no default rules, meaning if an interface doesn't match any rule, its profile remains unchanged (but you can create one by simply adding rules with the condition `Interface Name regex .*` at the end).
* **Lock** - When a profile is manually assigned to an interface, it is locked, and it will be skipped during classification. This is done to ensure that manual settings are not overridden.

### Available Conditions

Conditions (`Match Rules`) consist of specifying the interface Field for checking, the operation, and the values to which the operation is applied.

* **Field** - the interface attribute used for checking:
  * `Name` - interface name
  * `Description` - interface description
  * `IP Address` - interface IP address
  * `Tagged VLAN` - tagged VLAN
  * `Untagged VLAN` - untagged VLAN
* **Operation** `Operation` - the operation used for comparison:
  * `eq` - equality (Field equals)
  * `regexp` - regular expression match
  * `in` - inclusion (can only be used with `IP Address`, `Tagged VLAN`, `Untagged VLAN` fields)
* **Value** - the value for comparison by `eq` and `regex` operations
* **Prefix** - Prefix table (`IP Prefix`) is supported only for the `in` operation and the `IP Address` field. Configured in `Main -> Setup -> Prefix Tables`.
* **VLAN Filter** - [VLAN filter](../vc-filter/index.md) is supported only for the `in` operation and the `Tagged VLAN` and `Untagged VLAN` fields. Configured in `VC -> Setup -> VC Filters`.
* **Description** - explanations for the rule

Compatibility table of operations and values.

| Field         | eq  | regex | in                                                    |
| ------------- | --- | ----- | ----------------------------------------------------- |
| Name          | V   | V     | X                                                     |
| Description   | V   | V     | X                                                     |
| IP Address    | X   | X     | V (with the value `Prefix`)                           |
| Tagged VLAN   | X   | X     | V (with the value [VC Filter](../vc-filter/index.md)) |
| Untagged VLAN | V   | X     | V (with the value [VC Filter](../vc-filter/index.md)) |

<!-- prettier-ignore -->
!!! Info

  Only compatible fields and operations should be used. Failure to comply will result in an **NotImplemented Error** during classification.

