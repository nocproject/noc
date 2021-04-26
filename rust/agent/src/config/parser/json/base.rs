// ---------------------------------------------------------------------
// JsonParser
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Parser;
use crate::error::AgentError;
use crate::zk::ZkConfig;

pub struct JsonParser;

impl Parser for JsonParser {
    fn is_valid_extension(ext: &str) -> bool {
        match ext {
            "json" => true,
            _ => false,
        }
    }
    fn parse(data: &[u8]) -> Result<ZkConfig, AgentError> {
        match serde_json::from_slice(data) {
            Ok(x) => Ok(x),
            Err(e) => Err(AgentError::ParseError(e.to_string())),
        }
    }
}
