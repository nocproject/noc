# cpu Model Interface

CPU capabilities.

`arch` must be one of:

* `x86`  
* `x86_64`
* `PPC`  
* `PPC64`
* `ARM7` 
* `MIPS` 

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `arch` | str | CPU Architecture | {{ yes }} | {{ yes }} |
| `cores` | int | Effective number of cores. For bigLITTLE and similar, the maximal number of cores which may work similtaneously | {{ yes }} | {{ yes }} |
| `ht` | bool | Hyper-Threading support | {{ no }} | {{ yes }} |
| `freq` | int | Nominal frequence in MHz | {{ no }} | {{ yes }} |
| `turbo_freq` | int | Maximal frequence in MHz | {{ no }} | {{ yes }} |
| `l1_cache` | int | L1 cache size in kb | {{ no }} | {{ yes }} |
| `l2_cache` | int | L2 cache size in kb | {{ no }} | {{ yes }} |
| `l3_cache` | int | L3 cache size in kb | {{ no }} | {{ yes }} |

<!-- table end -->
