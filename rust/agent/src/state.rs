// ---------------------------------------------------------------------
// ZkState
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Serialize, Deserialize)]
pub struct AgentState {
    pub zeroconf_url: Option<String>,
    pub agent_id: Option<u64>,
    pub agent_key: Option<String>,
    #[serde(skip)]
    #[serde(default = "default_false")]
    is_dirty: bool,
}

impl Default for AgentState {
    fn default() -> Self {
        AgentState {
            zeroconf_url: None,
            agent_id: None,
            agent_key: None,
            is_dirty: false,
        }
    }
}

impl AgentState {
    pub fn from_file_or_default(path: Option<String>) -> Self {
        match path {
            Some(p) => Self::from_file(p),
            None => Self::default(),
        }
    }
    pub fn from_file(path: String) -> Self {
        match fs::read(&path) {
            Ok(data) => match serde_json::from_slice(&data) {
                Ok(state) => {
                    log::error!("Reading state from {}", path);
                    state
                }
                Err(e) => {
                    log::error!("Failed to decode state from {}: {}", path, e.to_string());
                    Self::default()
                }
            },
            Err(e) => {
                log::error!("Failed to read state from {}: {}", path, e.to_string());
                Self::default()
            }
        }
    }
    fn save(&self, path: String) -> Result<(), AgentError> {
        let data = serde_json::to_string(self)
            .map_err(|e| AgentError::SerializationError(e.to_string()))?;
        fs::write(path, data).map_err(AgentError::IoError)?;
        Ok(())
    }
    pub fn try_save(&mut self, path: Option<String>) {
        if !self.is_dirty {
            return;
        }
        match path {
            Some(p) => {
                log::info!("Saving state to {}", p);
                match self.save(p.clone()) {
                    Ok(_) => self.set_dirty(false),
                    Err(e) => log::info!("Failed to save state to {}: {}", p, e.to_string()),
                }
            }
            None => {
                log::info!("Cannot save state: No path");
                self.set_dirty(false);
            }
        }
    }
    fn set_dirty(&mut self, flag: bool) {
        self.is_dirty = flag;
    }
    pub fn has_url(&self) -> bool {
        self.zeroconf_url.is_some()
    }
    pub fn set_zeroconf_url(&mut self, url: String) -> &mut Self {
        if !self.is_dirty && self.zeroconf_url != Some(url.clone()) {
            self.set_dirty(true);
        }
        self.zeroconf_url = Some(url);
        self
    }
    pub fn set_agent_id(&mut self, agent_id: u64) -> &mut Self {
        if !self.is_dirty && self.agent_id != Some(agent_id) {
            self.set_dirty(true);
        }
        self.agent_id = Some(agent_id);
        self
    }
    pub fn set_agent_key(&mut self, agent_key: String) -> &mut Self {
        if !self.is_dirty && self.agent_key != Some(agent_key.clone()) {
            self.set_dirty(true);
        }
        self.agent_key = Some(agent_key);
        self
    }
}

fn default_false() -> bool {
    false
}
