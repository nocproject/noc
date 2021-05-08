// ---------------------------------------------------------------------
// block-io collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
pub use super::BlockIoOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

const NAME: &str = "block_io";

#[derive(Id, Repeatable)]
pub struct BlockIoCollector {
    pub id: String,
    pub service: String,
    pub interval: u64,
    pub labels: Vec<String>,
}

impl TryFrom<&ZkConfigCollector> for BlockIoCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::BlockIo(_) => Ok(Self {
                id: value.get_id(),
                service: value.get_service(),
                interval: value.get_interval(),
                labels: value.get_labels(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for BlockIoCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = self.get_timestamp();
        let stats = sys.block_device_statistics()?;
        for s in stats.values() {
            let mut labels = self.labels.clone();
            labels.push(format!("noc::dev::{}", s.name));
            self.feed(&BlockIoOut {
                ts: ts.clone(),
                service: self.service.clone(),
                collector: NAME,
                labels,
                //
                read_ios: s.read_ios,
                read_merges: s.read_merges,
                read_sectors: s.read_sectors,
                read_ticks: s.read_ticks,
                write_ios: s.write_ios,
                write_merges: s.write_merges,
                write_sectors: s.write_sectors,
                write_ticks: s.write_ticks,
                in_flight: s.in_flight,
                io_ticks: s.io_ticks,
                time_in_queue: s.time_in_queue,
            })
            .await?;
        }
        Ok(Status::Ok)
    }
}
