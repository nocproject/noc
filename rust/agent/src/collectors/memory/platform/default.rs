// ---------------------------------------------------------------------
// Non-specific memory information
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Serialize;
use std::convert::TryFrom;
use systemstat::PlatformMemory;

#[derive(Serialize)]
pub struct PlatformMemoryOut {}

impl TryFrom<&PlatformMemory> for PlatformMemoryOut {
    type Error = AgentError;

    fn try_from(value: &PlatformMemory) -> Result<PlatformMemoryOut, Self::Error> {
        Ok(PlatformMemoryOut {})
    }
}
