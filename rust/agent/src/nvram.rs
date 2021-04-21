// ---------------------------------------------------------------------
// agent::nvram module
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use crate::error::AgentError;
use serde::{Deserialize, Serialize};
use std::fs;

const NVRAM_PATH: &str = ".nvram";

#[derive(Serialize, Deserialize, Debug)]
pub struct Nvram {
    pub zeroconf_url: Option<String>,
    pub default_zeroconf_url: Option<String>,
}

impl Nvram {
    pub fn new() -> Self {
        Self {
            zeroconf_url: None,
            default_zeroconf_url: None,
        }
    }
    pub fn load(&mut self) -> Result<(), AgentError> {
        log::debug!("Loading NVRAM from {}", NVRAM_PATH);
        let raw_data = fs::read(NVRAM_PATH)?;
        let v: Nvram =
            serde_json::from_slice(&raw_data).map_err(|e| AgentError::ParseError(e.to_string()))?;
        self.zeroconf_url = v.zeroconf_url;
        self.default_zeroconf_url = v.default_zeroconf_url;
        Ok(())
    }
    pub fn save(&self) -> Result<(), AgentError> {
        log::debug!("Saving NVRAM to {}", NVRAM_PATH);
        let v = serde_json::to_string(&self).map_err(|e| AgentError::ParseError(e.to_string()))?;
        fs::write(NVRAM_PATH, v)?;
        Ok(())
    }
    pub fn set_zeroconf_url(&mut self, url: &str) -> Result<(), AgentError> {
        if self.zeroconf_url.is_some() && self.zeroconf_url.as_ref().unwrap() == url {
            return Ok(());
        }
        log::debug!("Setting zeroconf url to {}", url);
        self.zeroconf_url = Some(url.into());
        self.save()
    }
}

impl Default for Nvram {
    fn default() -> Self {
        Self::new()
    }
}
