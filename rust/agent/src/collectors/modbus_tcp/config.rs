// ---------------------------------------------------------------------
// ModbusTcpConfig
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::proto::modbus::ModbusFormat;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct ModbusTcpConfig {
    pub address: String,
    #[serde(default = "default_502")]
    pub port: u16,
    pub register: u16,
    // #[serde(flatten)]
    #[serde(default = "default_holding")]
    pub register_type: RegisterType,
    pub format: ModbusFormat,
}

#[derive(Deserialize, Debug, Clone)]
#[serde(rename_all = "lowercase")]
#[serde(tag = "request_type")]
pub enum RegisterType {
    Holding,
    Input,
    Coil,
}

fn default_502() -> u16 {
    502
}

fn default_holding() -> RegisterType {
    RegisterType::Holding
}
