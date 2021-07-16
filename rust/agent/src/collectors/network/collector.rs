// ---------------------------------------------------------------------
// network collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Schedule, Status};
use super::NetworkOut;
use crate::error::AgentError;
use async_trait::async_trait;
use systemstat::{Platform, System};

pub struct ConfigStub;
pub type NetworkCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for NetworkCollector {
    const NAME: &'static str = "network";
    type Output = NetworkOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let sys = System::new();
        let ts = Self::get_timestamp();
        let interfaces = sys
            .networks()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        for iface in interfaces.values() {
            let stats = sys
                .network_stats(&iface.name)
                .map_err(|e| AgentError::InternalError(e.to_string()))?;
            let mut labels = self.get_labels();
            labels.push(format!("noc::interface::{}", iface.name));
            self.feed(
                ts.clone(),
                labels,
                &NetworkOut {
                    //
                    rx_bytes: stats.rx_bytes.as_u64(),
                    tx_bytes: stats.tx_bytes.as_u64(),
                    rx_packets: stats.rx_packets,
                    tx_packets: stats.tx_packets,
                    rx_errors: stats.rx_errors,
                    tx_errors: stats.tx_errors,
                },
            )
            .await?;
        }
        Ok(Status::Ok)
    }
}
