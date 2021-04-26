// ---------------------------------------------------------------------
// File resolver
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Resolver;
use crate::cli::CliArgs;
use crate::config::reader::{ConfigReader, FileReader};
use crate::error::AgentError;
use std::convert::TryFrom;

pub struct StaticResolver {
    pub path: String,
}

impl TryFrom<CliArgs> for StaticResolver {
    type Error = AgentError;

    fn try_from(args: CliArgs) -> Result<StaticResolver, Self::Error> {
        match args.config {
            Some(path) => Ok(StaticResolver { path }),
            None => Err(AgentError::ConfigurationError(
                "--config option required".to_string(),
            )),
        }
    }
}

impl Resolver for StaticResolver {
    fn is_failable(&self) -> bool {
        false
    }
    fn is_repeatable(&self) -> bool {
        false
    }
    fn get_reader(&self) -> Result<ConfigReader, AgentError> {
        Ok(ConfigReader::File(FileReader {
            path: self.path.clone(),
        }))
    }
}
