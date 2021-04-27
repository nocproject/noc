// ---------------------------------------------------------------------
// Config Reader
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::FileReader;
use crate::config::ZkConfig;
use crate::error::AgentError;
use async_trait::async_trait;
use enum_dispatch::enum_dispatch;

#[enum_dispatch]
pub enum ConfigReader {
    File(FileReader),
}

#[async_trait]
#[enum_dispatch(ConfigReader)]
pub trait Reader {
    async fn get_config(&self) -> Result<ZkConfig, AgentError>;
}

impl ConfigReader {
    pub fn from_url(url: String) -> Option<ConfigReader> {
        match ConfigReader::get_schema(url.clone()) {
            Some(schema) => match &schema[..] {
                "file" => Some(ConfigReader::File(FileReader {
                    path: url[5..].into(),
                })),
                _ => None,
            },
            _ => None,
        }
    }
    fn get_schema(url: String) -> Option<String> {
        match url.find(":") {
            Some(pos) => Some(url[..pos].into()),
            None => None,
        }
    }
}

// Stub reader for disabled features
pub struct StubReader;

#[async_trait]
impl Reader for StubReader {
    async fn get_config(&self) -> Result<ZkConfig, AgentError> {
        Err(AgentError::FeatureDisabledError(
            "Feature is disabled".into(),
        ))
    }
}
