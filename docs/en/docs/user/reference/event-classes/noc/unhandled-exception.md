---
uuid: 1d279004-cd09-4382-a405-acea050775be
---
# NOC | Unhandled Exception

Unhandled Exception in NOC

## Symptoms

Unexpected behavior of NOC

## Probable Causes

Bug in NOC

## Recommended Actions

Grab this event, clear valuable data and submit an issue at http://nocproject.org/

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
component | str | {{ yes }} | NOC's component
traceback | str | {{ yes }} | Exception traceback
file | str | {{ no }} | Failed module
line | int | {{ no }} | Failed line
