// ---------------------------------------------------------------------
// Linux-specific memory information
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Serialize;
use std::convert::TryFrom;
use systemstat::PlatformMemory;

#[derive(Serialize, Default)]
pub struct PlatformMemoryOut {
    #[serde(skip_serializing_if = "Option::is_none")]
    active: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    active_anon: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    active_file: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    anon_huge_pages: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    anon_pages: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    bounce: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    buffer: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    cached: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    commit_limit: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    commit_as: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    direct_map_1g: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    direct_map_2m: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    direct_map_4k: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    dirty: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    file_huge_pages: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    file_pmd_mapped: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    huge_page_size: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    huge_tlb: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    inactive: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    inactive_anon: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    inactive_file: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    k_reclaimable: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    kernel_stack: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    mapped: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    mem_available: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    mem_free: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    mem_total: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    m_locked: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    nfs_unstable: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    page_tables: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    per_cpu: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    s_reclaimable: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    s_unreclaim: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sh_mem: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sh_mem_huge_pages: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sh_mem_pmd_mapped: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    slab: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    swap_cached: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    swap_free: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    swap_total: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    unevictable: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    vmalloc_chunk: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    vmalloc_total: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    vmalloc_used: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    writeback: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    writeback_tmp: Option<u64>,
}

impl TryFrom<&PlatformMemory> for PlatformMemoryOut {
    type Error = AgentError;

    fn try_from(value: &PlatformMemory) -> Result<PlatformMemoryOut, Self::Error> {
        let mut pm = PlatformMemoryOut::default();
        for (key, measure) in value.meminfo.iter() {
            let mv = measure.as_u64();
            match &key.to_lowercase()[..] {
                "active" => pm.active = Some(mv),
                "active(anon)" => pm.active_anon = Some(mv),
                "active(file)" => pm.active_file = Some(mv),
                "anonhugepages" => pm.anon_huge_pages = Some(mv),
                "anonpages" => pm.anon_pages = Some(mv),
                "bounce" => pm.bounce = Some(mv),
                "buffers" => pm.buffer = Some(mv),
                "cached" => pm.cached = Some(mv),
                "commitlimit" => pm.commit_limit = Some(mv),
                "committed_as" => pm.commit_as = Some(mv),
                "directmap1g" => pm.direct_map_1g = Some(mv),
                "directmap2m" => pm.direct_map_2m = Some(mv),
                "directmap4k" => pm.direct_map_4k = Some(mv),
                "dirty" => pm.dirty = Some(mv),
                "filehugepages" => pm.file_huge_pages = Some(mv),
                "filepmdmapped" => pm.file_pmd_mapped = Some(mv),
                "hugepagesize" => pm.huge_page_size = Some(mv),
                "hugetlb" => pm.huge_tlb = Some(mv),
                "inactive" => pm.inactive = Some(mv),
                "inactive(anon)" => pm.inactive_anon = Some(mv),
                "inactive(file)" => pm.inactive_file = Some(mv),
                "kreclaimable" => pm.k_reclaimable = Some(mv),
                "kernelstack" => pm.kernel_stack = Some(mv),
                "mapped" => pm.mapped = Some(mv),
                "memavailable" => pm.mem_available = Some(mv),
                "memfree" => pm.mem_free = Some(mv),
                "memtotal" => pm.mem_total = Some(mv),
                "mlocked" => pm.m_locked = Some(mv),
                "nfs_unstable" => pm.nfs_unstable = Some(mv),
                "pagetables" => pm.page_tables = Some(mv),
                "percpu" => pm.per_cpu = Some(mv),
                "sreclaimable" => pm.s_reclaimable = Some(mv),
                "sunreclaim" => pm.s_unreclaim = Some(mv),
                "shmem" => pm.sh_mem = Some(mv),
                "shmemhugepages" => pm.sh_mem_huge_pages = Some(mv),
                "shmempmdmapped" => pm.sh_mem_pmd_mapped = Some(mv),
                "slab" => pm.slab = Some(mv),
                "swapcached" => pm.swap_cached = Some(mv),
                "swapfree" => pm.swap_free = Some(mv),
                "swaptotal" => pm.swap_total = Some(mv),
                "unevictable" => pm.unevictable = Some(mv),
                "vmallocchunk" => pm.vmalloc_chunk = Some(mv),
                "vmalloctotal" => pm.vmalloc_total = Some(mv),
                "vmallocused" => pm.vmalloc_used = Some(mv),
                "writeback" => pm.writeback = Some(mv),
                "writebacktmp" => pm.writeback_tmp = Some(mv),
                _ => {}
            }
        }
        Ok(pm)
    }
}
