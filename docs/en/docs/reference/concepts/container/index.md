# Container

Container is a part of local logical hierarchy allowing to organize
[Managed Objects](../managed-object/index.md) in any desired way. Each container
can hold other containers building _container tree_. _Container tree_
is accessible via _Inventory_ `Web` of via `Card`

Container can be any of _Container Types_

## Root

Top-level of container hierarchy

## Group

Arbitrary group on any level of hierarchy

## Country

Start of political division representing given country.

## City

Start of geographic division representing city, town or any other type of habitation.

## Point of Presence

Point of Presence (PoP), i.e. the place where equipment is placed. PoPs
are distinguished by level, which it takes in network hierarchy. Possible
levels are (from top to bottom)

- `International` - PoP holds equipment for trans-border interconnects.
  Usually a subject for the national regulations.
- `National` - PoP holds equipment for trans-regional interconnects within
  the single country. May be subject for the national regulations.
- `Regional` - PoP holds equipment for inter-regional interconnects.
- `Core` - PoP holds local network core equipment.
- `Aggregation` - PoP holds utility equpment to aggregate customer connections
  before entering the core.
- `Access` - PoP holds equipment for customer access

PoPs are visible on geographic maps. Level of PoP is important to detect
zoom levels to show the PoP. `International` - level PoPs are visible ever
on worldwide scale, while `National` and `Region` may require additional zooming.
Even more zoom is required to show `Core` and `Aggregation` PoPs, while
`Access` level became visible on home- and block- scales.

## Floor

Represents single floor inside `PoP`

## Room

Represents a single room. May be nested into `Floor` or `Point of Presence`.

## Rack Row

A row of `Rack`, used for additional `Rack` grouping. May be nested into `Room`.

## Rack

Single equipment rack. May be nested into `Rack Row`, `Room` or into `Point of Presence`.
