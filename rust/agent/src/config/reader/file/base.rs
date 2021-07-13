// ---------------------------------------------------------------------
// File Reader
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Reader;
use crate::config::ConfigParser;
use crate::config::ZkConfig;
use crate::error::AgentError;
use async_trait::async_trait;
use std::fs;
use std::path::Path;

pub struct FileReader {
    path: String,
}

pub struct FileReaderBuilder {
    path: Option<String>,
}

impl FileReader {
    pub fn builder() -> FileReaderBuilder {
        FileReaderBuilder { path: None }
    }
}

impl FileReaderBuilder {
    pub fn with_path(&mut self, path: String) -> &mut Self {
        self.path = Some(path);
        self
    }
    pub fn build(&self) -> FileReader {
        FileReader {
            path: self.path.as_ref().unwrap().clone(),
        }
    }
}

#[async_trait]
impl Reader for FileReader {
    async fn get_config(&self) -> Result<ZkConfig, AgentError> {
        log::debug!("Reading config file: {}", self.path);
        match Path::new(&self.path).extension() {
            Some(ext) => {
                let x = ext.to_str().ok_or_else(|| {
                    AgentError::ConfigurationError("Cannot parse extension".to_string())
                })?;
                let data = fs::read(&self.path)?;
                ConfigParser::from_ext(data, x.into())
            }
            None => Err(AgentError::ParseError("Unknown format".to_string())),
        }
    }
}
