// ---------------------------------------------------------------------
// cpu collector implementation
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
use systemstat::{Platform, System};
use tokio::time::{sleep, Duration};

#[derive(Id, Repeatable)]
pub struct CpuCollector {
    pub id: String,
    pub interval: u64,
}

impl TryFrom<&ZkConfigCollector> for CpuCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Cpu(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for CpuCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let delayed_stats = sys
            .cpu_load()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Wait for CPU statistics been collected
        sleep(Duration::from_secs(1)).await;
        let stats = delayed_stats
            .done()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        log::debug!("Cpu usage: {:?}", stats);
        Ok(Status::Ok)
    }
}
