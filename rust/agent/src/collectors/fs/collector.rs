// ---------------------------------------------------------------------
// fs collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

#[derive(Id, Repeatable)]
pub struct FsCollector {
    pub id: String,
    pub interval: u64,
}

impl TryFrom<&ZkConfigCollector> for FsCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Fs(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for FsCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let mounts = sys
            .mounts()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        log::debug!("Filesystem usage:");
        for fs in mounts.iter() {
            log::debug!("Mount {:?}", fs);
        }
        Ok(Status::Ok)
    }
}
