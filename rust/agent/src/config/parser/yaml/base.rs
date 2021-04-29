// ---------------------------------------------------------------------
// YamlParser
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Parser;
use crate::config::ZkConfig;
use crate::error::AgentError;

pub struct YamlParser;

impl Parser for YamlParser {
    fn is_valid_extension(ext: &str) -> bool {
        matches!(ext, "yml" | "yaml")
    }
    fn parse(data: &[u8]) -> Result<ZkConfig, AgentError> {
        match serde_yaml::from_slice(data) {
            Ok(x) => Ok(x),
            Err(e) => Err(AgentError::ParseError(e.to_string())),
        }
    }
}
