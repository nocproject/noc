// ---------------------------------------------------------------------
// twamp_sender collector configuration
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::proto::pktmodel::ModelConfig;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct TwampSenderConfig {
    pub server: String,
    #[serde(default = "default_862")]
    pub port: u16,
    #[serde(default = "default_be")]
    pub dscp: String,
    pub n_packets: usize,
    // Model config
    #[serde(flatten)]
    pub model: ModelConfig,
}

fn default_862() -> u16 {
    862
}

fn default_be() -> String {
    "be".into()
}
