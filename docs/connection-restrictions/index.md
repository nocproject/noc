# Connection Restrictions

Real world does not allow connecting anything to anything. So inventory
_MUST_ enforce as many restrictions as possible. Connection restrictions
may be expressed in several complimentary ways:

- [Connection Restrictions](#connection-restrictions)
  - [Type](#type)
  - [Gender](#gender)
  - [Direction](#direction)
  - [Protocols](#protocols)
  - [Crossing](#crossing)
    - [Examples](#examples)
      - [DAC/Twinax cable](#dactwinax-cable)
      - [Unidirectional Splitter](#unidirectional-splitter)
      - [Bidirectional Splitter](#bidirectional-splitter)
      - [95%/5% splitter](#955-splitter)

The connection may be established only when all five kinds of restrictions are met.

## Type

[Connection Type](../connection-types-reference/index.md) restricts a physical type of
connection. I.e. meaningless to connect RJ-45 jack to C14 electrical socket.
The connection may be established only with the same or compatible types.

Connection type examples:

- [RJ45](../connection-types-reference/electrical.md#electrical-rj45)
- [C13](../connection-types-reference/power.md#power-iec-60320-c13)
- [C14](../connection-types-reference/power.md#power-iec-60320-c14)
- [LC](../connection-types-reference/optical.md#optical-lc)

Type may be considered as mechanical form-factor, something like the form, size,
and patterns of pins and holes.

Connection type compatibility may be complex.
See [Connection Type Restrictions discussion](../connection-type-restrictions/index.md)
for explanation.

## Gender

Connections of same [Connection Type](#type) may be symmetrical, or **genderless**;
or be of two mutual fitting sides (**male** and **female**). NOC supports 3 genders:

- `s` - genderless, or side connection.
- `m` - male connection.
- `f` - female connection.

Genders may be mated according the table:

|     | `s`       | `m`       | `f`       |
| --- | --------- | --------- | --------- |
| `s` | {{ yes }} | {{ no }}  | {{ no }}  |
| `m` | {{ no }}  | {{ no }}  | {{ yes }} |
| `f` | {{ no }}  | {{ yes }} | {{ no }}  |

Or mnemonically: side-to-side, male-to-female, female-to-male.
Unlike real life, NOC doesn't support advanced combinations of relations.

Males and females are equal in rights and the division is very arbitrary.

Possible genders on connections may be additionally restricted by Connection Types.
See [Genders Restriction Discussion](../connection-type-restrictions/index.md#gender-restrictions) for
additional explanation.

## Direction

Connection direction determines the hierarchy of the connected object. NOC supports
three directions:

- `i` - Inwards: The connected object will be put inside the current one.
- `o` - Outwards: The current object will be put inside the connected one.
- `s` - Side: Objects will be connected but neither object will be put inside the peer one.

`i` connections are usually slots for various extension modules, line cards, PSU e.t.c.
They allow the gaining of additional features by putting something inside.

`o` connections are usually extension modules themselves. They should be put
into something to became valuable.

`s` connections are neither previous cases. They are used to connect the object
with the outer world. Various cables, patch cords, power cables are good examples
of `s` connections.

`s` connections utilize genders, while the gender of `i` and `o` connections
is only conventional. `i` connections are usually females, while `o` are male ones.

Directions can be connected by following way:

|     | `s`       | `i`       | `o`       |
| --- | --------- | --------- | --------- |
| `s` | {{ yes }} | {{ no }}  | {{ no }}  |
| `i` | {{ no }}  | {{ no }}  | {{ yes }} |
| `o` | {{ no }}  | {{ yes }} | {{ no }}  |

Or mnemonically: side-to-side, inwards-to-outwards, outwards-to-inwards. Following
chart explains inwards-to-outwards kind of relation:

![I/O Direction](direction-io.svg){: width=300px }

Unlike the genders, directions are rarely misused.

## Protocols

While types, genders, and directions are merely physical properties, which
can easily be observed with the naked eye, protocols define agreements on
electrical, optical, and other kinds of signals. Connection is the physical
media, while protocols are the logical use of it.

Consider example: RJ-45 port (Connection type `Electrical | RJ45`, gender `female`, direction `side`)
is only the hole in the box. It may serve as an ethernet port: maybe 10Mbit/s, or 100Mbit/s,
or gigabit one. It may provide or consume power over PoE. It may be a console port, utilizing RS-232 serial protocol.
It may support 2 or 4-wire RS-485 serial protocol. It may be dumb passive cross-panel
entry, leading floors away. You still may plug RJ-45 jack anyway, but will be any use of that?

So the protocols define possible usage of connection.
Refer to the [Inventory Protocols](../inventory-protocols-reference/index.md) for
the full list of protocols, provided by NOC. Protocols may be symmetric,
when both peers utilizing the same configuration, like autoconfigured ethernet ports.
Protocols may be asymmetric, like PoE consumer and PoE provider, RS-232 DTU and DCU.

Asymmetric protocols are denoted by `>` and `<` prefix, like '>RS-232' and '<RS-232'.
`>` leads inside the protocol, meaning that it will be consumed.
i.e. '>POE' means that the device may consume power over PoE over the given connection.
`<` leads outside the protocol, meaning that it will be provided.
i.e. '<POE' means that the device can provide power over PoE over the given connection.
The protocol without `>` and `<` can be provided and consumed as well.

Protocols are gender-agnostic. i.e. RS-232 DCU may use DB-9 male or female sockets
as well.

The connection may support several protocols, i.e. ethernet may be coupled with PoE,
and so on.

`i` and `o` directions enforce strict protocol match. `i` connection may
provide at least one protocol which peer's `o` connection may consume or vise versa.
`s` connections may provide protocols, or be protocol-agnostic with empty protocols list.
Protocol-agnostic connections dependency will be described later.

Protocol compatibility matrix:

|      | Both      | `>`       | `<`       |
| ---- | --------- | --------- | --------- |
| Both | {{ yes }} | {{ yes }} | {{ yes }} |
| `>`  | {{ yes }} | {{ no }}  | {{ yes }} |
| `<`  | {{ yes }} | {{yes }}  | {{ no }}  |

Mnemonic rules: Pure providers shall not be mated with pure providers,
pure consumers shall not be mated with pure consumers.

Protocol-agnostic connections are the proxies or the media. They cannot
deal with the protocol itself, but they can transport protocol to a connection,
which can handle it. The best example of protocol-agnostic connections
is the cable. It has two ends, and it can transport signal to the other end.
Transport capabilities and restrictions are discussed in the [Crossing](#crossing) section.

Protocol-agnostic connections are traced to the other ends and cannot be
connected only in one of two cases:

- Provided or consumed protocol can be traced to compatible endpoint (`s` port with compatible protocol).
- Provided or consumed protocol cannot be traced to the endpoint with any other protocol. (dark fibre principe).

## Crossing

The crossing is the additional set of rules which can be applied to protocol-agnostic
`s` connections within the same object to define the possible protocol flow.
Usually, crossing represents static multiplexing which can be defined o model
or object level. Static multiplexing means the signal with given protocol
may pass trannsparently from input to one or more output slots.

Crossing is defined as table of items, each connects particular input with
particular output. Additonal restrictions, named discriminators, are possible.

| Name                   | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `input`                | Input connection name                                       |
| `input_discriminator`  | Optional input discriminator                                |
| `output`               | Output connection name                                      |
| `output_discriminator` | Optional output discriminator, for describe output mappings |
| `gain_db`              | Signal gain, in dB                                          |

!!! note
    Unlike other restrictions, which defines the object's communications
    with the outer world (extravertive nature), crossing defines an object's
    internals (introvertive nature).

The common rules of the signal passing are:

``` mermaid
flowchart TD
    start((start))
    c_input{`input` matched?}
    c_input_discriminator{Has input_discriminator?}
    c_input_match{Input discriminator matched?}
    skip([Skip Rule])
    passed([Signal Passed to output])
    start --> c_input
    c_input -- Yes --> c_input_discriminator
    c_input -- No --> skip
    c_input_discriminator -- Yes --> c_input_match
    c_input_discriminator -- No --> passed
    c_input_match -- Yes --> passed
    c_input_match -- No --> skip
```

Signal is replicated to all matched outputs. Additionaly, signal gain/loss may be applied.


### Examples

#### DAC/Twinax cable

| Input | Output |
| ----- | ------ |
| `s1`  | `s2`   |
| `s2`  | `s1`   |

``` mermaid
graph LR
    s1 --> s2
    s2 --> s1
```

#### Unidirectional Splitter

1:4 splitter with equal distribution

| Input | Output | Gain (dB) |
| ----- | ------ | --------- |
| `in`  | `out1` | `-6`      |
| `in`  | `out2` | `-6`      |
| `in`  | `out3` | `-6`      |
| `in`  | `out4` | `-6`      |

``` mermaid
graph LR
in -- -6dB --> out1
in -- -6dB --> out2
in -- -6dB --> out3
in -- -6dB --> out4
```

#### Bidirectional Splitter

1:4 splitter with equal distribution in dowstream,
allowing to pass signal upstream with 3 dB attenuation.

| Input  | Output | Gain (dB) |
| ------ | ------ | --------- |
| `in`   | `out1` | `-6`      |
| `in`   | `out2` | `-6`      |
| `in`   | `out3` | `-6`      |
| `in`   | `out4` | `-6`      |
| `out1` | `in`   | `-3`      |
| `out2` | `in`   | `-3`      |
| `out3` | `in`   | `-3`      |
| `out4` | `in`   | `-3`      |

``` mermaid
graph LR
in -- -6dB --> out1
in -- -6dB --> out2
in -- -6dB --> out3
in -- -6dB --> out4
out1 -- -3dB --> in
out2 -- -3dB --> in
out3 -- -3dB --> in
out4 -- -3dB --> in
```

#### 95%/5% splitter

Common TV system splitter, passing 95% of the signal to transit
and redirecting 5% to output.

| Input | Output    | Gain     |
| ----- | --------- | -------- |
| `in`  | `transit` | `-0.2`   |
| `in`  | `out`     | `-139.8` |

``` mermaid
graph LR
in -- -0.2dB --> transit
in -- -139.8dB --> output
```
