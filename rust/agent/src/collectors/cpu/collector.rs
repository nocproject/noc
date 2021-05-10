// ---------------------------------------------------------------------
// cpu collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Schedule, Status};
use super::{CpuOut, PlatformCpuOut};
use crate::error::AgentError;
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};
use tokio::time::{sleep, Duration};

pub struct ConfigStub;
pub type CpuCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for CpuCollector {
    const NAME: &'static str = "cpu";
    type Output = CpuOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = Self::get_timestamp();
        let delayed_stats = sys
            .cpu_load()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Wait for CPU statistics been collected
        sleep(Duration::from_secs(1)).await;
        let stats = delayed_stats
            .done()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        for (i, s) in stats.iter().enumerate() {
            let mut labels = self.get_labels();
            labels.push(format!("noc::cpu::{}", i));
            self.feed(
                ts.clone(),
                labels,
                &CpuOut {
                    // Common
                    // Metrics
                    user: s.user,
                    nice: s.nice,
                    system: s.system,
                    interrupt: s.interrupt,
                    idle: s.idle,
                    platform: PlatformCpuOut::try_from(&s.platform)?,
                },
            )
            .await?;
        }
        Ok(Status::Ok)
    }
}
