// ---------------------------------------------------------------------
// cpu collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use super::{CpuOut, PlatformCpuOut};
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};
use tokio::time::{sleep, Duration};

const NAME: &str = "cpu";

#[derive(Id, Repeatable)]
pub struct CpuCollector {
    pub id: String,
    pub interval: u64,
    pub labels: Vec<String>,
}

impl TryFrom<&ZkConfigCollector> for CpuCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Cpu(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
                labels: value.labels.clone(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for CpuCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = self.get_timestamp();
        let delayed_stats = sys
            .cpu_load()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Wait for CPU statistics been collected
        sleep(Duration::from_secs(1)).await;
        let stats = delayed_stats
            .done()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        for (i, s) in stats.iter().enumerate() {
            let mut labels = self.labels.clone();
            labels.push(format!("noc::cpu::{}", i));
            self.feed(&CpuOut {
                // Common
                ts: ts.clone(),
                collector: NAME,
                labels,
                // Metrics
                user: s.user,
                nice: s.nice,
                system: s.system,
                interrupt: s.interrupt,
                idle: s.idle,
                platform: PlatformCpuOut::try_from(&s.platform)?,
            })
            .await?;
        }
        Ok(Status::Ok)
    }
}
