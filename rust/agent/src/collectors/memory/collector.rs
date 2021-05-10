// ---------------------------------------------------------------------
// memory collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Status};
use super::{MemoryOut, PlatformMemoryOut};
use crate::error::AgentError;
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

pub struct ConfigStub;
pub type MemoryCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for MemoryCollector {
    const NAME: &'static str = "memory";

    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = Self::get_timestamp();
        let memory = sys
            .memory()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        self.feed(&MemoryOut {
            // Common
            ts: ts.clone(),
            service: self.get_service(),
            collector: Self::get_name(),
            labels: self.get_labels(),
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
