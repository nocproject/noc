// ---------------------------------------------------------------------
// File Reader
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Reader;
use crate::config::ConfigParser;
use crate::error::AgentError;
use crate::zk::ZkConfig;
use async_trait::async_trait;
use std::fs;
use std::path::Path;

pub struct FileReader {
    pub path: String,
}

#[async_trait]
impl Reader for FileReader {
    async fn get_config(&self) -> Result<ZkConfig, AgentError> {
        log::debug!("Reading config file: {}", self.path);
        match Path::new(&self.path).extension() {
            Some(ext) => {
                let x = ext.to_str().ok_or(AgentError::ConfigurationError(
                    "Cannot parse extension".to_string(),
                ))?;
                let data = fs::read(&self.path)?;
                ConfigParser::from_ext(data, x.into())
            }
            None => Err(AgentError::ParseError("Unknown format".to_string())),
        }
    }
}
