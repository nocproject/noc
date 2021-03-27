---
uuid: ca079994-9417-44c8-bddc-95e94d4f85e6
---
# Interface | xDSL | Line | Errors | SES | Delta Metric Type

Count of seconds during this interval where there was:
ATU-C:(CRC-8 summed over all bearer channels) >=18 OR
LOS >=1 OR SEF >=1 OR LPR >=1
ATU-R:(FEBE summed over all bearer channels) >=18 OR
LOS-FE >=1 OR RDI >=1 OR LPR-FE >=1 .
This parameter is inhibited during UAS.

## Data Model

Scope
: [Interface](../../../../../../scopes/interface.md)

Field
: `xdsl_line_errors_ses_delta`

Type
: UInt32

Measure
: `count`
