// ---------------------------------------------------------------------
// <describe module here>
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::JsonParser;
use super::YamlParser;
use crate::error::AgentError;
use crate::zk::ZkConfig;

pub enum ConfigParser {
    Json(JsonParser),
    Yaml(YamlParser),
}

pub trait Parser {
    // Check if extension is valid for format
    fn is_valid_extension(_ext: &str) -> bool {
        false
    }
    fn parse(data: &[u8]) -> Result<ZkConfig, AgentError>;
}

impl ConfigParser {
    pub fn from_ext(data: Vec<u8>, ext: String) -> Result<ZkConfig, AgentError> {
        let e: &str = ext.as_str();
        let d = data.as_slice();
        if JsonParser::is_valid_extension(e) {
            return JsonParser::parse(d);
        }
        if YamlParser::is_valid_extension(e) {
            return YamlParser::parse(d);
        }
        Err(AgentError::ParseError("Unknown format".to_string()))
    }
}
//
pub struct StubParser;

impl Parser for StubParser {
    fn parse(_data: &[u8]) -> Result<ZkConfig, AgentError> {
        Err(AgentError::FeatureDisabledError(
            "Parser is disabled".to_string(),
        ))
    }
}
