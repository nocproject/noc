# confdb

`noc confdb` - ConfDB manipulation tool

## Synopsis

    noc confdb syntax [path ...]
               tokenizer [--object=<id>|--profile=<profile> --config=<path>]
               normalizer [--object=<id>|--profile=<profile> --config=<path>]

## Description

ConfDB investigation tool

## Examples

Dump ConfDB syntax:

    ./noc confdb syntax

Dump part of ConfDB syntax:

    ./noc confdb syntax intefaces x

Dump result of object's [tokenizer](../../../dev/reference/confdb/tokenizer.md).
Managed Object ID is 120:

    ./noc confdb tokenizer --object=120

Dump result of object's [tokenizer](../../../dev/reference/confdb/tokenizer.md),
applied to arbitrary file:

    ./noc confdb tokenizer --object=120 --config=config.txt

Dump result of profile's [tokenizer](../../../dev/reference/confdb/tokenizer.md),
applied to arbitrary file:

    ./noc confdb tokenizer --profile=Cisco.IOS --config=config.txt

Dump result of object's [normalizer](../../../dev/reference/confdb/normalizer.md).
Managed Object ID is 120:

    ./noc confdb normalizer --object=120

Dump result of object's [normalizer](../../../dev/reference/confdb/normalizer.md),
applied to arbitrary file:

    ./noc confdb normalizer --object=120 --config=config.txt

Dump result of profile's [normalizer](../../../dev/reference/confdb/normalizer.md),
applied to arbitrary file:

    ./noc confdb normalizer --profile=Cisco.IOS --config=config.txt

## See also
* [ConfDB Syntax Reference](../../../dev/reference/confdb/index.md)
* [ConfDB Normalizers](../../../dev/reference/confdb/normalizer.md)
* [ConfDB Tokenizers](../../../dev/reference/confdb/tokenizer.md)
