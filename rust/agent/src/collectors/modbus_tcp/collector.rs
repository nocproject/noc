// ---------------------------------------------------------------------
// ModbusTcpCollector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::{Collectable, Collector, CollectorConfig, Schedule, Status};
use super::config::RegisterType;
use super::ModbusTcpOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use crate::proto::modbus::ModbusFormat;
use async_trait::async_trait;
use std::convert::TryFrom;
use std::net::SocketAddr;
use tokio::time::{timeout, Duration};
use tokio_modbus::prelude::*;

pub struct ModbusTcpCollectorConfig {
    addr: SocketAddr,
    register: u16,
    count: u16,
    register_type: RegisterType,
    format: ModbusFormat,
    timeout_ms: u64,
    slave: u8,
}
pub type ModbusTcpCollector = Collector<ModbusTcpCollectorConfig>;

impl TryFrom<&ZkConfigCollector> for ModbusTcpCollectorConfig {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::ModbusTcp(config) => {
                let addr = format!("{}:{}", config.address, config.port)
                    .parse()
                    .map_err(|_| AgentError::ParseError("cannot parse address".to_string()))?;
                Ok(Self {
                    addr,
                    register: config.register,
                    count: config.format.min_count(),
                    register_type: config.register_type.clone(),
                    format: config.format,
                    timeout_ms: config.timeout_ms,
                    slave: config.slave,
                })
            }
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

#[async_trait]
impl Collectable for ModbusTcpCollector {
    const NAME: &'static str = "modbus-tcp";
    type Output = ModbusTcpOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let ts = Self::get_timestamp();
        // Connect the server
        log::debug!(
            "[{}] Sending request to {}, start={:#X}, count={}",
            self.id,
            self.data.addr,
            self.data.register,
            self.data.count
        );
        let mut ctx = tcp::connect_slave(self.data.addr, Slave::from(self.data.slave))
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Read result
        let duration = Duration::from_millis(self.data.timeout_ms);
        let data = match self.data.register_type {
            RegisterType::Holding => timeout(
                duration,
                ctx.read_holding_registers(self.data.register, self.data.count),
            )
            .await?
            .map_err(|e| AgentError::InternalError(e.to_string()))?,
            RegisterType::Input => timeout(
                duration,
                ctx.read_input_registers(self.data.register, self.data.count),
            )
            .await?
            .map_err(|e| AgentError::InternalError(e.to_string()))?,
            RegisterType::Coil => timeout(
                duration,
                ctx.read_coils(self.data.register, self.data.count),
            )
            .await?
            .map_err(|e| AgentError::InternalError(e.to_string()))?
            .iter()
            .map(|v| if *v { 1 } else { 0 })
            .collect(),
        };
        // Process input value
        let value = self.data.format.modbus_try_from(data)?;
        //
        self.feed(ts.clone(), self.get_labels(), &ModbusTcpOut { value })
            .await?;
        Ok(Status::Ok)
    }
}
