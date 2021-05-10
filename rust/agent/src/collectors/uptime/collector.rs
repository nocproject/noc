// ---------------------------------------------------------------------
// uptime collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Schedule, Status};
use super::UptimeOut;
use crate::error::AgentError;
use async_trait::async_trait;
use systemstat::{Platform, System};

pub struct ConfigStub;
pub type UptimeCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for UptimeCollector {
    const NAME: &'static str = "uptime";
    type Output = UptimeOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let ts = Self::get_timestamp();
        // Collect uptime
        let sys = System::new();
        let uptime = sys
            .uptime()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Prepare output
        self.feed(
            ts,
            self.get_labels(),
            &UptimeOut {
                uptime: uptime.as_secs(),
            },
        )
        .await?;
        Ok(Status::Ok)
    }
}
