// ---------------------------------------------------------------------
// ZkConfig
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
pub struct ZkConfig {
    #[serde(rename = "$version")]
    _version: String,
    #[serde(rename = "$type")]
    _type: String,
    pub config: ZkConfigConfig,
    pub collectors: Vec<ZkConfigCollector>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ZkConfigConfig {
    pub zeroconf: ZkConfigConfigZeroconf,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ZkConfigConfigZeroconf {
    pub interval: u64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ZkConfigCollector {
    pub id: String,
    #[serde(rename = "type")]
    pub collector_type: String,
    pub interval: u64,
    #[serde(default)]
    pub disabled: bool,
    #[serde(flatten)]
    pub config: HashMap<String, Value>,
}

impl ZkConfig {
    pub fn new_from(data: Vec<u8>) -> Result<Self, Box<dyn Error>> {
        match serde_json::from_slice(data.as_slice()) {
            Ok(x) => Ok(x),
            Err(e) => {
                log::error!("Cannot parse JSON: {}", e);
                Err("Cannot parse JSON".into())
            }
        }
    }
}

pub trait Configurable<TCfg>
where
    TCfg: DeserializeOwned,
{
    fn get_config(cfg: &HashMap<String, serde_json::Value>) -> Result<TCfg, Box<dyn Error>> {
        let c_value = serde_json::to_value(&cfg)?;
        Self::get_config_from_value(c_value)
    }
    fn get_config_from_value(cfg: serde_json::Value) -> Result<TCfg, Box<dyn Error>> {
        match serde_json::from_value::<TCfg>(cfg) {
            Ok(x) => Ok(x),
            Err(e) => Err(Box::new(e)),
        }
    }
}
