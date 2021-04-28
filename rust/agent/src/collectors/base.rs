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
pub trait Collectable {
    // Get current timestamp in RFC-3339 format
    fn get_timestamp(&self) -> String {
        let t: DateTime<Utc> = SystemTime::now().into();
        t.to_rfc3339_opts(SecondsFormat::Millis, false)
    }
    // Feed collected data
    async fn feed<T>(&self, data: &T) -> Result<(), AgentError>
    where
        T: Serialize + Sync,
    {
        let out = serde_json::to_string(data)
            .map_err(|e| AgentError::SerializationError(e.to_string()))?;
        log::debug!("Out: {}", out);
        Ok(())
    }
    // Collection cycle
    async fn collect(&self) -> Result<Status, AgentError>;
}

/// Helper trait for implicit collector implementation.
pub trait Id {
    fn get_id(&self) -> String;
}

/// Helper trait for implicit collector implementation.
pub trait Repeatable {
    fn get_interval(&self) -> u64;
}

#[async_trait]
impl<T> Runnable for T
where
    T: Id + Repeatable + Collectable + Send + Sync,
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

/// Stub collectors are used to substitute collectors disabled in compile time.
pub struct StubCollector<TCfg> {
    pub id: String,
    _phantom: PhantomData<TCfg>,
}

impl<TCfg> TryFrom<&ZkConfigCollector> for StubCollector<TCfg> {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        Ok(Self {
            id: value.id.clone(),
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
