// ---------------------------------------------------------------------
// ModbusRtuCollector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::{Collectable, Collector, CollectorConfig, Schedule, Status};
use super::config::{CfgParity, RegisterType};
use super::ModbusRtuOut;
use crate::config::ZkConfigCollector;
use crate::error::AgentError;
use crate::proto::modbus::ModbusFormat;
use async_trait::async_trait;
use std::convert::TryFrom;
use tokio_modbus::prelude::*;
use tokio_serial::{DataBits, Parity, SerialPortBuilderExt, StopBits};

pub struct ModbusRtuCollectorConfig {
    serial_path: String,
    slave: Slave,
    baud_rate: u32,
    data_bits: DataBits,
    parity: Parity,
    stop_bits: StopBits,
    register: u16,
    count: u16,
    register_type: RegisterType,
    format: ModbusFormat,
}
pub type ModbusRtuCollector = Collector<ModbusRtuCollectorConfig>;

impl TryFrom<&ZkConfigCollector> for ModbusRtuCollectorConfig {
    type Error = AgentError;

    fn try_from(value: &ZkConfigCollector) -> Result<Self, Self::Error> {
        match &value.config {
            CollectorConfig::ModbusRtu(config) => {
                let data_bits = match config.data_bits {
                    5 => DataBits::Five,
                    6 => DataBits::Six,
                    7 => DataBits::Seven,
                    8 => DataBits::Eight,
                    _ => return Err(AgentError::ParseError("invalid data_bits".to_string())),
                };
                let parity = match config.parity {
                    CfgParity::None => Parity::None,
                    CfgParity::Odd => Parity::Odd,
                    CfgParity::Even => Parity::Even,
                };
                let stop_bits = match config.stop_bits {
                    1 => StopBits::One,
                    2 => StopBits::Two,
                    _ => return Err(AgentError::ParseError("invalid stop_bits".to_string())),
                };
                let min_count = config.format.min_count();
                let count = if config.count >= min_count {
                    config.count
                } else {
                    min_count
                };
                Ok(Self {
                    serial_path: config.serial_path.clone(),
                    slave: Slave::from(config.slave),
                    baud_rate: config.baud_rate,
                    data_bits,
                    parity,
                    stop_bits,
                    register: config.register,
                    count,
                    register_type: config.register_type.clone(),
                    format: config.format,
                })
            }
            _ => Err(AgentError::ConfigurationError("invalid config".into())),
        }
    }
}

impl ModbusRtuCollector {
    fn serial_settings(&self) -> String {
        let data_bits = match self.data.data_bits {
            DataBits::Five => 5,
            DataBits::Six => 6,
            DataBits::Seven => 7,
            DataBits::Eight => 8,
        };
        let parity = match self.data.parity {
            Parity::None => "N",
            Parity::Even => "E",
            Parity::Odd => "O",
        };
        let stop_bits = match self.data.stop_bits {
            StopBits::One => 1,
            StopBits::Two => 2,
        };
        format!(
            "{}@{} ({}{}{})",
            self.data.serial_path, self.data.baud_rate, data_bits, parity, stop_bits
        )
    }
}

#[async_trait]
impl Collectable for ModbusRtuCollector {
    const NAME: &'static str = "modbus-rtu";
    type Output = ModbusRtuOut;

    async fn collect(&self) -> Result<Status, AgentError> {
        let ts = Self::get_timestamp();
        // Connect the serial port
        log::debug!("[{}] Setting up serial {}", self.id, self.serial_settings());
        let port = tokio_serial::new(self.data.serial_path.clone(), self.data.baud_rate)
            .data_bits(self.data.data_bits)
            .parity(self.data.parity)
            .stop_bits(self.data.stop_bits)
            .open_native_async()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Sending request
        log::debug!(
            "[{}] Sending RTU request to slave {}",
            self.id,
            self.data.slave
        );
        let mut ctx = rtu::connect_slave(port, self.data.slave)
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        // Read result
        let data = match self.data.register_type {
            RegisterType::Holding => ctx
                .read_holding_registers(self.data.register, self.data.count)
                .await
                .map_err(|e| AgentError::InternalError(e.to_string()))?,
            RegisterType::Input => ctx
                .read_input_registers(self.data.register, self.data.count)
                .await
                .map_err(|e| AgentError::InternalError(e.to_string()))?,
            RegisterType::Coil => ctx
                .read_coils(self.data.register, self.data.count)
                .await
                .map_err(|e| AgentError::InternalError(e.to_string()))?
                .iter()
                .map(|v| if *v { 1 } else { 0 })
                .collect(),
        };
        log::debug!("[{}] Modbus response: {:?}", self.id, data);
        // Process input value
        let value = self.data.format.modbus_try_from(data)?;
        //
        self.feed(ts.clone(), self.get_labels(), &ModbusRtuOut { value })
            .await?;
        Ok(Status::Ok)
    }
}
