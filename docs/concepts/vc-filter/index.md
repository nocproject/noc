# VC Filter

`VC Filter` is named VLAN filters which can be reused in many places

## Expression Syntax
`VC Filter` expression syntax:
```
<vcfilter> ::= <item> [',' <vcfilter>]
<item> ::= <vlan> | <range>
<vlan> ::= [0-9]+
<range> ::= <vlan> '-' <vlan>
```

## Examples
* `1-4095` - any VLAN
* `100-200,300,1000` - VLAN numbers from 100 to 200 (inclusive), as well as 300 and 1000
* `1` - only VLAN 1

# Settings

The VLAN Filters are located in  `VC` -> `Setup` -> `VC Filter`.

![VC Filter edit form](vc-filter-any-vlan-form.png)

* `Name` - VLAN name
* `Description` - description
* `Expression` - VLAN set expression
