// ---------------------------------------------------------------------
// ZkConfig
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::collectors::CollectorConfig;
use crate::error::AgentError;
use serde::Deserialize;
use std::convert::TryFrom;

#[derive(Deserialize, Debug)]
pub struct ZkConfig {
    #[serde(rename = "$version")]
    _version: String,
    #[serde(rename = "$type")]
    _type: String,
    pub config: ZkConfigConfig,
    pub collectors: Vec<ZkConfigCollector>,
}

#[derive(Deserialize, Debug)]
pub struct ZkConfigConfig {
    pub zeroconf: ZkConfigConfigZeroconf,
}

#[derive(Deserialize, Debug)]
pub struct ZkConfigConfigZeroconf {
    pub interval: u64,
}

#[derive(Deserialize, Debug)]
pub struct ZkConfigCollector {
    pub id: String,
    pub interval: u64,
    #[serde(default)]
    pub disabled: bool,
    #[serde(flatten)]
    pub config: CollectorConfig,
}

impl TryFrom<Vec<u8>> for ZkConfig {
    type Error = AgentError;

    fn try_from(value: Vec<u8>) -> Result<Self, Self::Error> {
        match serde_json::from_slice(value.as_slice()) {
            Ok(x) => Ok(x),
            Err(e) => {
                log::error!("Cannot parse JSON: {}", e);
                Err(AgentError::ParseError(e.to_string()))
            }
        }
    }
}
