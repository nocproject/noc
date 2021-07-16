# memory collector

`memory` collects usage statistics.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `memory`                                                                            |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |

## Collected Metrics

| Metric           | Metric Type | Platform | Description        |
| ---------------- | ----------- | -------- | ------------------ |
| `ts`             |             | All      | ISO 8601 Timestamp |
| `collector`      |             | All      | Collector Id       |
| `labels`         |             | All      | List of labels     |
| `total`          |             | All      |                    |
| `free`           |             | All      |                    |
|                  |             |          |                    |
| `active`         |             | Linux    |                    |
| `active(anon)`   |             | Linux    |                    |
| `active(file)`   |             | Linux    |                    |
| `anonhugepages`  |             | Linux    |                    |
| `anonpages`      |             | Linux    |                    |
| `bounce`         |             | Linux    |                    |
| `buffers`        |             | Linux    |                    |
| `cached`         |             | Linux    |                    |
| `commitlimit`    |             | Linux    |                    |
| `committed_as`   |             | Linux    |                    |
| `directmap1g`    |             | Linux    |                    |
| `directmap2m`    |             | Linux    |                    |
| `directmap4k`    |             | Linux    |                    |
| `dirty`          |             | Linux    |                    |
| `filehugepages`  |             | Linux    |                    |
| `filepmdmapped`  |             | Linux    |                    |
| `hugepagesize`   |             | Linux    |                    |
| `hugetlb`        |             | Linux    |                    |
| `inactive`       |             | Linux    |                    |
| `inactive(anon)` |             | Linux    |                    |
| `inactive(file)` |             | Linux    |                    |
| `kreclaimable`   |             | Linux    |                    |
| `kernelstack`    |             | Linux    |                    |
| `mapped`         |             | Linux    |                    |
| `memavailable`   |             | Linux    |                    |
| `memfree`        |             | Linux    |                    |
| `memtotal`       |             | Linux    |                    |
| `mlocked`        |             | Linux    |                    |
| `nfs_unstable`   |             | Linux    |                    |
| `pagetables`     |             | Linux    |                    |
| `percpu`         |             | Linux    |                    |
| `sreclaimable`   |             | Linux    |                    |
| `sunreclaim`     |             | Linux    |                    |
| `shmem`          |             | Linux    |                    |
| `shmemhugepages` |             | Linux    |                    |
| `shmempmdmapped` |             | Linux    |                    |
| `slab`           |             | Linux    |                    |
| `swapcached`     |             | Linux    |                    |
| `swapfree`       |             | Linux    |                    |
| `swaptotal`      |             | Linux    |                    |
| `unevictable`    |             | Linux    |                    |
| `vmallocchunk`   |             | Linux    |                    |
| `vmalloctotal`   |             | Linux    |                    |
| `vmallocused`    |             | Linux    |                    |
| `writeback`      |             | Linux    |                    |
| `writebacktmp`   |             | Linux    |                    |
|                  |             |          |                    |
| `active`         |             | FreeBSD  |                    |
| `inactive`       |             | FreeBSD  |                    |
| `wired`          |             | FreeBSD  |                    |
| `cache`          |             | FreeBSD  |                    |
| `zfs_arc`        |             | FreeBSD  |                    |
|                  |             |          |                    |
| `active`         |             | OpenBSD  |                    |
| `inactive`       |             | OpenBSD  |                    |
| `wired`          |             | OpenBSD  |                    |
| `cache`          |             | OpenBSD  |                    |
| `paging`         |             | OpenBSD  |                    |
|                  |             |          |                    |
| `active`         |             | MacOS    |                    |
| `inactive`       |             | MacOS    |                    |
| `wired`          |             | MacOS    |                    |
| `cache`          |             | MacOS    |                    |
|                  |             |          |                    |
| `load`           |             | Windows  |                    |
| `total_phys`     |             | Windows  |                    |
| `avail_phys`     |             | Windows  |                    |
| `total_pagefile` |             | Windows  |                    |
| `avail_pagefile` |             | Windows  |                    |
| `total_virt`     |             | Windows  |                    |
| `avail_virt`     |             | Windows  |                    |
| `avail_ext`      |             | Windows  |                    |

## Compilation Features

Enable `memory` feature during compiling the agent (Enabled by default).
