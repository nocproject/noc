---
uuid: 39854dc7-40bd-46d6-96eb-ed4d950312d7
---
# Network | OAM | Client Clear Remote Failure

Client has received a message to clear remote failure indication from its remote peer

## Symptoms

## Probable Causes

The remote client received a message to clear a link fault, or a dying gasp (an unrecoverable local failure), or a critical event in the operations, administration, and maintenance Protocol Data Unit (OAMPDU).

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
reason | str | {{ no }} | Failure reason
