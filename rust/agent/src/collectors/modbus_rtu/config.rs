// ---------------------------------------------------------------------
// ModbusRtuConfig
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::proto::modbus::ModbusFormat;
use serde::Deserialize;
use std::hash::Hash;

#[derive(Deserialize, Debug, Clone, Hash)]
pub struct ModbusRtuConfig {
    pub serial_path: String,
    pub slave: u8,
    pub baud_rate: u32,
    pub data_bits: usize, // 5,6,7,8
    #[serde(default = "default_none")]
    pub parity: CfgParity,
    pub stop_bits: usize, // 1, 2
    pub register: u16,
    #[serde(default = "default_holding")]
    pub register_type: RegisterType,
    pub format: ModbusFormat,
    #[serde(default = "default_5000")]
    pub timeout_ms: u64,
}

#[derive(Deserialize, Debug, Clone, Hash)]
#[serde(rename_all = "lowercase")]
#[serde(tag = "request_type")]
pub enum RegisterType {
    Holding,
    Input,
    Coil,
}

#[derive(Deserialize, Debug, Clone, Hash)]
#[serde(rename_all = "lowercase")]
#[serde(tag = "parity")]
pub enum CfgParity {
    None,
    Odd,
    Even,
}

fn default_holding() -> RegisterType {
    RegisterType::Holding
}

fn default_none() -> CfgParity {
    CfgParity::None
}

fn default_5000() -> u64 {
    5_000
}
