// ---------------------------------------------------------------------
// Config Reader
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{FileReader, HttpReader};
use crate::config::ZkConfig;
use crate::error::AgentError;
use crate::state::AgentState;
use crate::sysid::SysId;
use async_trait::async_trait;
use enum_dispatch::enum_dispatch;

#[enum_dispatch]
pub enum ConfigReader {
    File(FileReader),
    Http(HttpReader),
}

#[async_trait]
#[enum_dispatch(ConfigReader)]
pub trait Reader {
    async fn get_config(&self) -> Result<ZkConfig, AgentError>;
}

impl ConfigReader {
    pub fn from_url(
        url: String,
        sys_id: Option<&SysId>,
        state: Option<&AgentState>,
        validate_cert: bool,
    ) -> Option<ConfigReader> {
        match ConfigReader::get_schema(url.clone()) {
            Some(schema) => match &schema[..] {
                "file" => Some(ConfigReader::File(
                    FileReader::builder().with_path(url[5..].into()).build(),
                )),
                "http" | "https" => Some(ConfigReader::Http(
                    HttpReader::builder()
                        .with_path(url)
                        .with_cert_validation(validate_cert)
                        .with_agent_state(state)
                        .with_sys_id(sys_id)
                        .build(),
                )),

                _ => None,
            },
            None => Some(ConfigReader::File(
                FileReader::builder().with_path(url).build(),
            )),
        }
    }
    fn get_schema(url: String) -> Option<String> {
        url.find(':').map(|pos| url[..pos].into())
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
