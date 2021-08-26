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
    pub metrics: Option<ZkConfigMetrics>,
}

#[derive(Deserialize, Debug)]
pub struct ZkConfigConfigZeroconf {
    pub id: Option<u64>,     // Agent id
    pub key: Option<String>, // Agent auth key
    pub interval: u64,
}

#[derive(Deserialize, Debug, Clone)]
pub struct ZkConfigMetrics {
    #[serde(rename = "type")]
    pub _type: String, // must be metricscollector
    pub url: String,
    pub batch_size: Option<usize>,
    pub send_delay_ms: Option<u64>,
    pub retry_timeout_ms: Option<u64>,
}

#[derive(Deserialize, Debug, Hash)]
pub struct ZkConfigCollector {
    pub id: String,
    pub service: u64,
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
    pub fn get_service(&self) -> u64 {
        self.service
    }
    pub fn get_interval(&self) -> u64 {
        self.interval
    }
    pub fn get_labels(&self) -> Vec<String> {
        self.labels.clone()
    }
}
