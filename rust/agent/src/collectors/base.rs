// ---------------------------------------------------------------------
// Collector generic
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::zk::ZkConfigCollector;
use async_trait::async_trait;
use enum_dispatch::enum_dispatch;
use rand::Rng;
use std::error::Error;
use std::marker::PhantomData;
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
#[enum_dispatch(Collectors)]
pub trait Runnable {
    async fn run(&self) -> ();
}

#[async_trait]
pub trait Collectable {
    async fn collect(&self) -> Result<Status, Box<dyn Error>>;
}

pub trait Configurable {
    fn prepare(&mut self) -> Result<(), Box<dyn Error>> {
        Ok(())
    }
}

impl<TCfg> Collector<TCfg>
where
    TCfg: Configurable + Clone,
{
    pub fn new_from(zk: &ZkConfigCollector, c: TCfg) -> Result<Self, Box<dyn Error>> {
        let mut config = c.clone(); // second clone for a while
        config.prepare()?;
        Ok(Self {
            id: zk.id.clone(),
            interval: zk.interval,
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

/// Stub collectors are used to substitute collectors disabled in compile time.
pub struct StubCollector<TCfg> {
    pub id: String,
    _phantom: PhantomData<TCfg>,
}

impl<TCfg> StubCollector<TCfg>
where
    TCfg: Configurable + Clone,
{
    pub fn new_from(zk: &ZkConfigCollector, _c: TCfg) -> Result<Self, Box<dyn Error>> {
        Ok(Self {
            id: zk.id.clone(),
            _phantom: PhantomData,
        })
    }
}

#[async_trait]
impl<TCfg> Runnable for StubCollector<TCfg>
where
    TCfg: Sync,
{
    async fn run(&self) {
        log::debug!(
            "[{}] Collector is not included in this build of agent. Skipping",
            self.id
        );
    }
}
