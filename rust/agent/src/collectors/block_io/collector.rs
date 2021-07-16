// ---------------------------------------------------------------------
// block-io collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Schedule, Status};
pub use super::BlockIoOut;
use crate::error::AgentError;
use async_trait::async_trait;
use systemstat::{Platform, System};

pub struct ConfigStub;
pub type BlockIoCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for BlockIoCollector {
    const NAME: &'static str = "block_io";
    type Output = BlockIoOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = Self::get_timestamp();
        let stats = sys.block_device_statistics()?;
        for s in stats.values() {
            let mut labels = self.get_labels();
            labels.push(format!("noc::dev::{}", s.name));
            self.feed(
                ts.clone(),
                labels,
                &BlockIoOut {
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
                },
            )
            .await?;
        }
        Ok(Status::Ok)
    }
}
