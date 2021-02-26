// ---------------------------------------------------------------------
// Collector generic
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::zk::{Configurable, ZkConfigCollector};
use async_trait::async_trait;
use rand::Rng;
use serde::de::DeserializeOwned;
use std::error::Error;
use tokio::time::Duration;

#[derive(Debug)]
pub enum Status {
    Ok,
    Warn,
    Fail,
}

pub struct Collector<TCfg> {
    pub id: String,
    pub interval: u64,
    pub config: TCfg,
}

#[async_trait]
pub trait Runnable {
    async fn run(&self) -> ();
}

#[async_trait]
pub trait Collectable {
    async fn collect(&self) -> Result<Status, Box<dyn Error>>;
}

impl<TCfg> Collector<TCfg>
where
    TCfg: Configurable<TCfg> + DeserializeOwned,
{
    pub fn new_from(cfg: &ZkConfigCollector) -> Result<Self, Box<dyn Error>> {
        let c = TCfg::get_config(&cfg.config)?;
        Ok(Self {
            id: cfg.id.clone(),
            interval: cfg.interval,
            config: c,
        })
    }
}

#[async_trait]
impl<TCfg> Runnable for Collector<TCfg>
where
    Collector<TCfg>: Collectable + Send,
    TCfg: Sync,
{
    async fn run(&self) {
        log::debug!("[{}] Starting collector", self.id);
        // Sleep random time to prevent spikes of load
        let delay: u64 = {
            let max_delay = self.interval * 1_000_000_000;
            rand::thread_rng().gen_range(0..max_delay)
        };
        log::debug!(
            "[{}] Starting delay {:?} of {:?}",
            &self.id,
            Duration::from_nanos(delay),
            Duration::from_secs(self.interval)
        );
        tokio::time::sleep(Duration::from_nanos(delay)).await;
        let sleep_duration = Duration::from_secs(self.interval);
        loop {
            log::info!("[{}] Collecting", self.id);
            match &self.collect().await {
                Ok(s) => log::info!("[{}] Complete with status {:?}", self.id, s),
                Err(e) => log::error!("[{}] Crashed with: {}", self.id, e),
            }
            tokio::time::sleep(sleep_duration).await;
        }
    }
}
