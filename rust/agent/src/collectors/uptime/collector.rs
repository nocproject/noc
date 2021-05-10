// ---------------------------------------------------------------------
// uptime collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Status};
use super::UptimeOut;
use crate::error::AgentError;
use async_trait::async_trait;
use systemstat::{Platform, System};

pub struct ConfigStub;
pub type UptimeCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for UptimeCollector {
    const NAME: &'static str = "uptime";

    async fn collect(&self) -> Result<Status, AgentError> {
        let ts = Self::get_timestamp();
        // Collect uptime
        let sys = System::new();
        let uptime = sys
            .uptime()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Prepare output
        self.feed(&UptimeOut {
            ts,
            service: self.get_service(),
            collector: Self::get_name(),
            labels: self.get_labels(),
            uptime: uptime.as_secs(),
        })
        .await?;
        Ok(Status::Ok)
    }
}
