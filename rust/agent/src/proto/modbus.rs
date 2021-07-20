// ---------------------------------------------------------------------
// Modbus data
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone, Copy)]
pub enum ModbusFormat {
    #[serde(rename = "i16_be")]
    I16Be,
    #[serde(rename = "u16_be")]
    U16Be,
}

impl ModbusFormat {
    pub fn modbus_try_from(self, v: Vec<u16>) -> Result<f64, AgentError> {
        match self {
            ModbusFormat::I16Be => ModbusFormat::from_i16_be(v),
            ModbusFormat::U16Be => ModbusFormat::from_u16_be(v),
        }
    }
    pub fn min_count(self) -> u16 {
        match self {
            ModbusFormat::I16Be => 1,
            ModbusFormat::U16Be => 1,
        }
    }
    pub fn from_i16_be(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.is_empty() {
            return Err(AgentError::ParseError("empty data".to_string()));
        }
        Ok(v[0] as i16 as f64)
    }
    pub fn from_u16_be(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.is_empty() {
            return Err(AgentError::ParseError("empty data".to_string()));
        }
        Ok(v[0] as f64)
    }
}
