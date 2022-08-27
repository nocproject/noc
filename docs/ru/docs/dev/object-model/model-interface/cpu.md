---
---

# cpu Model Interface

CPU capabilities

## Variables

| Name          | Type        | Description                     | Required         | Constant         | Default |
| ------------- | ----------- | ------------------------------- | ---------------- | ---------------- | ------- |
| arch          | String      | Architecture:                   | {{ yes }} | {{ yes }} |         |
|               |             |                                 |                  |                  |         |
|               |             | * `x86`                         |                  |                  |         |
|               |             | * `x86_64`                      |                  |                  |         |
|               |             | * `PPC`                         |                  |                  |         |
|               |             | * `PPC64`                       |                  |                  |         |
|               |             | * `ARM7`                        |                  |                  |         |
|               |             | * `MIPS`                        |                  |                  |         |
| cores         | Integer     | Effective number of cores.      | {{ yes }} | {{ yes }} |         |
|               |             | For bigLITTLE and similar,      |                  |                  |         |
|               |             | effective number of cores is 2  |                  |                  |         |
|               |             | rather than 4                   |                  |                  |         |
| ht            | Boolean     | Hyper Theading support          | {{ no }} | {{ yes }} |         |
| freq          | Integer     | Nominal frequence in MHz        | {{ no }} | {{ yes }} |         |
| turbo_freq    | Integer     | Maximal frequence in MHz        | {{ no }} | {{ yes }} |         |
| l1_cache      | Integer     | L1 cache size in kb             | {{ no }} | {{ yes }} |         |
| l2_cache      | Integer     | L2 cache size in kb             | {{ no }} | {{ yes }} |         |
| l3_cache      | Integer     | L3 cache size in kb             | {{ no }} | {{ yes }} |         |
