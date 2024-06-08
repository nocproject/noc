# hwlimits Model Interface

Interface be able to describe the hardware limits of the devices in the inventory models.
Limits can be set both on the chassis and for individual modules. Since the combination of module limits for modular equipment depends on too many factors, it is proposed not to implement it and to limit the control of limits for each individual module.

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `macs` | int | Limit for MAC addresses | {{ no }} | {{ yes }} |
| `queues` | int | Limit for QoS queues | {{ no }} | {{ yes }} |
| `ipv4_prefixes` | int | Limit for IPv4 prefixes | {{ no }} | {{ yes }} |
| `ipv6_prefixes` | int | Limit for IPv6 prefixes | {{ no }} | {{ yes }} |

<!-- table end -->

## Examples

```json
{
  "hwlimits": {
    "macs": 8192,
    "queues": 8,
    "ipv4_prefixes": 4294967295,
    "ipv6_prefixes": 4294967295
  }
}
```
