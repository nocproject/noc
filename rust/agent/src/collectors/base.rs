// ---------------------------------------------------------------------
// Collector generic
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use async_trait::async_trait;
use chrono::{DateTime, SecondsFormat, Utc};
use enum_dispatch::enum_dispatch;
use rand::Rng;
use serde::Serialize;
use std::convert::TryFrom;
use std::marker::PhantomData;
use std::time::SystemTime;
use tokio::time::Duration;

#[derive(Debug)]
pub enum Status {
    Ok,
    Warn,
    Fail,
}

/// .run() method for collector.
/// Take note on enum_dispatch.
/// Collector must implement either:
/// * Runnable trait (explicit)
/// * Collectable + Id + Repeatable (implicit)
#[async_trait]
#[enum_dispatch(Collectors)]
pub trait Runnable {
    async fn run(&self) -> ();
}

/// .collect() method for implicit implementation.
/// Must be used along with Id and Repeatable traits
#[async_trait]
pub trait Collectable: Schedule {
    const NAME: &'static str;
    type Output: Serialize + Sync;

    fn get_name() -> &'static str {
        Self::NAME
    }
    fn get_timestamp() -> String {
        let t: DateTime<Utc> = SystemTime::now().into();
        t.to_rfc3339_opts(SecondsFormat::Millis, false)
    }
    // Collection cycle
    async fn collect(&self) -> Result<Status, AgentError>;
    // Feed result
    async fn feed(
        &self,
        ts: String,
        labels: Vec<String>,
        data: &Self::Output,
    ) -> Result<(), AgentError> {
        let r = Output::<Self::Output> {
            ts,
            service: self.get_service(),
            collector: Self::get_name(),
            labels,
            data,
        };
        let out =
            serde_json::to_string(&r).map_err(|e| AgentError::SerializationError(e.to_string()))?;
        log::debug!("Out: {}", out);
        Ok(())
    }
}

/// Collector's schedule attributes
pub trait Schedule {
    fn get_id(&self) -> String;
    fn get_interval(&self) -> u64;
    fn get_service(&self) -> String;
    fn get_labels(&self) -> Vec<String>;
}

#[async_trait]
impl<T> Runnable for T
where
    T: Schedule + Collectable + Send + Sync,
{
    async fn run(&self) {
        let id = self.get_id();
        let interval = self.get_interval();
        log::debug!("[{}] Starting collector", id);
        // Sleep random time to prevent spikes of load
        let delay: u64 = {
            let max_delay = interval * 1_000_000_000;
            rand::thread_rng().gen_range(0..max_delay)
        };
        log::debug!(
            "[{}] Starting delay {:?} of {:?}",
            &id,
            Duration::from_nanos(delay),
            Duration::from_secs(interval)
        );
        tokio::time::sleep(Duration::from_nanos(delay)).await;
        let sleep_duration = Duration::from_secs(interval);
        loop {
            log::info!("[{}] Collecting", id);
            match &self.collect().await {
                Ok(s) => log::info!("[{}] Complete with status {:?}", id, s),
                Err(e) => log::error!("[{}] Crashed with: {}", id, e),
            }
            tokio::time::sleep(sleep_duration).await;
        }
    }
}

// Collector generics
// T - additional collector config and state
pub struct Collector<T> {
    pub id: String,
    pub service: String,
    pub interval: u64,
    pub labels: Vec<String>,
    pub data: T,
}

impl<T> TryFrom<&ZkConfigCollector> for Collector<T>
where
    T: for<'a> TryFrom<&'a ZkConfigCollector, Error = AgentError>,
{
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(Self {
            id: value.get_id(),
            service: value.get_service(),
            interval: value.get_interval(),
            labels: value.get_labels(),
            data: T::try_from(value)?,
        })
    }
}

// @todo: Move to Collector
impl<T> Schedule for Collector<T> {
    fn get_id(&self) -> String {
        self.id.clone()
    }
    fn get_interval(&self) -> u64 {
        self.interval
    }
    fn get_service(&self) -> String {
        self.service.clone()
    }
    fn get_labels(&self) -> Vec<String> {
        self.labels.clone()
    }
}

// Empty config for collector
pub type NoConfig<T> = PhantomData<T>;

impl<T> TryFrom<&ZkConfigCollector> for NoConfig<T> {
    type Error = AgentError;

    fn try_from(_value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(Self {})
    }
}

#[derive(Serialize)]
pub struct Output<'a, T>
where
    T: Serialize + Sync,
{
    pub ts: String,
    pub service: String,
    pub collector: &'static str,
    pub labels: Vec<String>,
    #[serde(flatten)]
    pub data: &'a T,
}

/// Stub collectors are used to substitute collectors disabled in compile time.
pub struct StubCollector<TCfg> {
    pub id: String,
    _phantom: PhantomData<TCfg>,
}

impl<TCfg> TryFrom<&ZkConfigCollector> for StubCollector<TCfg> {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(Self {
            id: value.get_id(),
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
