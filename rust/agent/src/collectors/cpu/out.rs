// ---------------------------------------------------------------------
// CpuOut
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::PlatformCpuOut;
use serde::Serialize;

#[derive(Serialize)]
pub struct CpuOut {
    pub user: f32,
    pub nice: f32,
    pub system: f32,
    pub interrupt: f32,
    pub idle: f32,
    #[serde(flatten)]
    pub platform: PlatformCpuOut,
}
