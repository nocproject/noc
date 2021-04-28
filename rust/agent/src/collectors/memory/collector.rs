// ---------------------------------------------------------------------
// memory collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use super::{MemoryOut, PlatformMemoryOut};
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

const NAME: &str = "memory";

#[derive(Id, Repeatable)]
pub struct MemoryCollector {
    pub id: String,
    pub interval: u64,
    pub labels: Vec<String>,
}

impl TryFrom<&ZkConfigCollector> for MemoryCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Memory(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
                labels: value.labels.clone(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for MemoryCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = self.get_timestamp();
        let memory = sys
            .memory()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        self.feed(&MemoryOut {
            // Common
            ts: ts.clone(),
            collector: NAME,
            labels: self.labels.clone(),
            //
            total: memory.total.as_u64(),
            free: memory.free.as_u64(),
            //
            platform: PlatformMemoryOut::try_from(&memory.platform_memory)?,
        })
        .await?;
        Ok(Status::Ok)
    }
}
