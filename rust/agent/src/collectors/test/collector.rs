// ---------------------------------------------------------------------
// test collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use crate::error::AgentError;
use crate::zk::ZkConfigCollector;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;

#[derive(Id, Repeatable)]
pub struct TestCollector {
    pub id: String,
    pub interval: u64,
}

impl TryFrom<&ZkConfigCollector> for TestCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Test(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
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
