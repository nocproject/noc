// ---------------------------------------------------------------------
// twamp_sender collector configuration
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Configurable;
use crate::proto::pktmodel::ModelConfig;
use crate::proto::tos::dscp_to_tos;
use serde::Deserialize;
use std::error::Error;

#[derive(Deserialize, Debug, Clone)]
pub struct TWAMPSenderConfig {
    pub server: String,
    #[serde(default = "default_862")]
    pub port: u16,
    #[serde(default = "default_be")]
    pub dscp: String,
    pub n_packets: usize,
    // test_timeout: u64,
    // Model config
    #[serde(flatten)]
    pub model: ModelConfig,
    // Internal fields
    #[serde(skip)]
    pub tos: u8,
}

impl Configurable for TWAMPSenderConfig {
    fn prepare(&mut self) -> Result<(), Box<dyn Error>> {
        self.tos = dscp_to_tos(self.dscp.to_lowercase()).ok_or("invalid dscp")?;
        Ok(())
    }
}

fn default_862() -> u16 {
    862
}

fn default_be() -> String {
    "be".into()
}
