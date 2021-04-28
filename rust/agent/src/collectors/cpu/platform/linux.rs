// ---------------------------------------------------------------------
// Linux-dependent Cpu information
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Serialize;
use std::convert::TryFrom;
use systemstat::PlatformCpuLoad;

#[derive(Serialize)]
pub struct PlatformCpuOut {
    pub iowait: f32,
}

impl TryFrom<&PlatformCpuLoad> for PlatformCpuOut {
    type Error = AgentError;

    fn try_from(value: &PlatformCpuLoad) -> Result<PlatformCpuOut, Self::Error> {
        Ok(PlatformCpuOut {
            iowait: value.iowait,
        })
    }
}
