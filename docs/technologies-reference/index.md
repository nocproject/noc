# Technologies Reference

Technology is an abstraction which implies restriction
on [Resource Groups](../concepts/resource-group/index.md), 
their *Services* and *Clients* and
their connections. See [appropriate concepts section](../concepts/technology/index.md)
for details.

## Built-in Technologies

The following technologies are provided out-of-the box:

<!-- table start -->
| Name                                                               | Description                                           | Service<br>Model | Client<br>Model  | Single<br>Service | Single<br>Client | Allow<br>Children |
| ------------------------------------------------------------------ | ----------------------------------------------------- | ---------------- | ---------------- | ----------------- | ---------------- | ----------------- |
| <a id="group"></a>Group                                            | Grouping element                                      |                  |                  | {{ no }}          | {{ no }}         | {{ yes }}         |
| <a id="network-cgnat-termination"></a>Network \| CGNAT Termination | CGNAT Temination (access equipment -> NAT equipment)  | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="network-controller"></a>Network \| Controller               | Controller - CPE relation                             | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ yes }}        | {{ no }}          |
| <a id="network-dpi-termination"></a>Network \| DPI Termination     | DPI Temination (access equipment -> DPI equipment)    | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="network-ipoe-termination"></a>Network \| IPoE Termination   | IPoE Temination (access equipment -> BRAS)            | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="network-pppoe-termination"></a>Network \| PPPoE Termination | PPPoE Temination (access equipment -> BRAS)           | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="network-pptp-termination"></a>Network \| PPTP Termination   | PPTP Temination (access equipment -> BRAS)            | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="network-traffic-group"></a>Network \| Traffic Group         | Group of Managed Objects for network planning tasks   | sa.ManagedObject |                  | {{ no }}          | {{ no }}         | {{ yes }}         |
| <a id="object-group"></a>Object Group                              | Arbitrary group of Managed Objects                    | sa.ManagedObject |                  | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="voice-h.248-termination"></a>Voice \| H.248 Termination     | H.248/MEGACO Temination (media gateway -> softswitch) | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="voice-h.323-termination"></a>Voice \| H.323 Termination     | H.323 Temination (media gateway -> softswitch)        | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="voice-mgcp-termination"></a>Voice \| MGCP Termination       | MGCP Temination (media gateway -> softswitch)         | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |
| <a id="voice-sip-termination"></a>Voice \| SIP Termination         | SIP Temination (media gateway -> softswitch)          | sa.ManagedObject | sa.ManagedObject | {{ no }}          | {{ no }}         | {{ no }}          |

<!-- table end -->