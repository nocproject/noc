// ---------------------------------------------------------------------
// MacOS-specific memory information
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
    pub active: u64,
    pub inactive: u64,
    pub wired: u64,
    pub cache: u64,
}

impl TryFrom<&PlatformMemory> for PlatformMemoryOut {
    type Error = AgentError;

    fn try_from(value: &PlatformMemory) -> Result<PlatformMemoryOut, Self::Error> {
        Ok(PlatformMemoryOut {
            active: value.active.as_u64(),
            inactive: value.inactive.as_u64(),
            wired: value.wired.as_u64(),
            cache: value.cache.as_u64(),
        })
    }
}
