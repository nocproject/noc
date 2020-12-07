

# whois


## Name
*whois* - WhoisCache manipulation utility

## Synopsis

    noc whois update-cache
    noc whois prefix-list [--name=<name>] [--profile=<profile>] <as-set>


## Description
#### update-cache

Download and update whois cache

#### prefix-list

Prefix-list builder. Where
* `<name>` - Name of prefix list to generate
* `<profile>` - SA Profile to use as formatter ([Cisco.IOS](../../../user/reference/profiles/Cisco/Cisco.IOS.md) by default)
* `<as-set>` - AS-set name

## Examples

Download and fill whois cache


    noc whois update-cache

Build Cisco-style prefix list


    noc whois prefix-list --name=my-prefix-list --profile=Cisco.IOS AS-EXAMPLE

Build JUNOS-style prefix list

    noc whois prefix-list --name=my-prefix-list --profile=Juniper.JUNOS AS-EXAMPLE


## See also
