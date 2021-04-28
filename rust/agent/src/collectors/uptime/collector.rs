// ---------------------------------------------------------------------
// uptime collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use super::UptimeOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

const NAME: &str = "uptime";

#[derive(Id, Repeatable)]
pub struct UptimeCollector {
    pub id: String,
    pub interval: u64,
    pub labels: Vec<String>,
}

impl TryFrom<&ZkConfigCollector> for UptimeCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Uptime(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
                labels: value.labels.clone(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for UptimeCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let ts = self.get_timestamp();
        // Collect uptime
        let sys = System::new();
        let uptime = sys
            .uptime()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Prepare output
        self.feed(&UptimeOut {
            ts,
            collector: NAME,
            labels: self.labels.clone(),
            uptime: uptime.as_secs(),
        })
        .await?;
        Ok(Status::Ok)
    }
}
