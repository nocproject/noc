// ---------------------------------------------------------------------
// network collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, CollectorConfig, Id, Repeatable, Status};
use super::NetworkOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use agent_derive::{Id, Repeatable};
use async_trait::async_trait;
use std::convert::TryFrom;
use systemstat::{Platform, System};

const NAME: &str = "network";

#[derive(Id, Repeatable)]
pub struct NetworkCollector {
    pub id: String,
    pub interval: u64,
    pub labels: Vec<String>,
}

impl TryFrom<&ZkConfigCollector> for NetworkCollector {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::Network(_) => Ok(Self {
                id: value.id.clone(),
                interval: value.interval,
                labels: value.labels.clone(),
            }),
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for NetworkCollector {
    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = self.get_timestamp();
        let interfaces = sys
            .networks()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        for iface in interfaces.values() {
            let stats = sys
                .network_stats(&iface.name)
                .map_err(|e| AgentError::InternalError(e.to_string()))?;
            let mut labels = self.labels.clone();
            labels.push(format!("noc::interface::{}", iface.name));
            self.feed(&NetworkOut {
                ts: ts.clone(),
                collector: NAME,
                labels,
                //
                rx_bytes: stats.rx_bytes.as_u64(),
                tx_bytes: stats.tx_bytes.as_u64(),
                rx_packets: stats.rx_packets,
                tx_packets: stats.tx_packets,
                rx_errors: stats.rx_errors,
                tx_errors: stats.tx_errors,
            })
            .await?;
        }
        Ok(Status::Ok)
    }
}
