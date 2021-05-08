// ---------------------------------------------------------------------
// ZkConfig
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::collectors::CollectorConfig;
use serde::Deserialize;

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
    #[serde(default)]
    pub service: Option<String>,
    pub interval: u64,
    #[serde(default)]
    pub disabled: bool,
    #[serde(default)]
    pub labels: Vec<String>,
    #[serde(flatten)]
    pub config: CollectorConfig,
}

impl ZkConfigCollector {
    pub fn get_id(&self) -> String {
        self.id.clone()
    }
    pub fn get_service(&self) -> String {
        match &self.service {
            Some(x) => x.into(),
            None => self.get_id(),
        }
    }
    pub fn get_interval(&self) -> u64 {
        self.interval
    }
    pub fn get_labels(&self) -> Vec<String> {
        self.labels.clone()
    }
}
