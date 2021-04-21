// ---------------------------------------------------------------------
// network collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use crate::error::AgentError;
use crate::zk::ZkConfigCollector;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

#[derive(Id, Repeatable)]
pub struct NetworkCollector {
    pub id: String,
    pub interval: u64,
}

impl TryFrom<&ZkConfigCollector> for NetworkCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Network(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for NetworkCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let interfaces = sys
            .networks()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        log::debug!("Network usage:");
        for iface in interfaces.values() {
            let stats = sys
                .network_stats(&iface.name)
                .map_err(|e| AgentError::InternalError(e.to_string()));
            log::debug!("Interface {} ({:?}): {:?}", iface.name, iface.addrs, stats);
        }
        Ok(Status::Ok)
    }
}
