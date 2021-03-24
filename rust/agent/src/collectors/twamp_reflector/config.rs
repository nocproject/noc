// ---------------------------------------------------------------------
// twamp_reflector collector configuration
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Configurable;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct TWAMPReflectorConfig {
    pub listen: String,
    #[serde(default = "default_862")]
    pub port: u16,
}

impl Configurable for TWAMPReflectorConfig {}

fn default_862() -> u16 {
    862
}
