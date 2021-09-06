// ---------------------------------------------------------------------
// twamp_sender collector configuration
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::proto::pktmodel::ModelConfig;
use serde::Deserialize;
use std::hash::Hash;

#[derive(Deserialize, Debug, Clone, Hash)]
pub struct TwampSenderConfig {
    pub server: String,
    #[serde(default = "default_862")]
    pub port: u16,
    #[serde(default = "default_0")]
    pub reflector_port: u16,
    #[serde(default = "default_be")]
    pub dscp: String,
    pub n_packets: usize,
    // Model config
    #[serde(flatten)]
    pub model: ModelConfig,
}

fn default_0() -> u16 {
    0
}

fn default_862() -> u16 {
    862
}

fn default_be() -> String {
    "be".into()
}
