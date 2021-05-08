// ---------------------------------------------------------------------
// test collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;

#[derive(Id, Repeatable)]
pub struct TestCollector {
    pub id: String,
    pub service: String,
    pub interval: u64,
}

impl TryFrom<&ZkConfigCollector> for TestCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Test(_) => Ok(Self {
                id: value.get_id(),
                service: value.get_service(),
                interval: value.get_interval(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for TestCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        Ok(Status::Ok)
    }
}
