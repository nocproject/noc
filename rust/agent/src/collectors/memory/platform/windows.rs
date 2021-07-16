// ---------------------------------------------------------------------
// Windows-specific memory information
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Serialize;
use std::convert::TryFrom;
use systemstat::PlatformMemory;

#[derive(Serialize)]
pub struct PlatformMemoryOut {
    pub load: u32,
    pub total_phys: u64,
    pub avail_phys: u64,
    pub total_pagefile: u64,
    pub avail_pagefile: u64,
    pub total_virt: u64,
    pub avail_virt: u64,
    pub avail_ext: u64,
}

impl TryFrom<&PlatformMemory> for PlatformMemoryOut {
    type Error = AgentError;

    fn try_from(value: &PlatformMemory) -> Result<PlatformMemoryOut, Self::Error> {
        Ok(PlatformMemoryOut {
            load: value.load,
            total_phys: value.total_phys.as_u64(),
            avail_phys: value.avail_phys.as_u64(),
            total_pagefile: value.total_pagefile.as_u64(),
            avail_pagefile: value.avail_pagefile.as_u64(),
            total_virt: value.total_virt.as_u64(),
            avail_virt: value.avail_virt.as_u64(),
            avail_ext: value.avail_ext.as_u64(),
        })
    }
}
