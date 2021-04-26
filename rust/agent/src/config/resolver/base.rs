// ---------------------------------------------------------------------
// Config resolver
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{StaticResolver, ZkResolver};
use crate::cli::CliArgs;
use crate::config::ConfigReader;
use crate::error::AgentError;
use crate::zk::ZkConfig;
use async_trait::async_trait;
use enum_dispatch::enum_dispatch;
use std::convert::TryFrom;

// Possible resolvers
#[enum_dispatch]
pub enum ConfigResolver {
    File(StaticResolver),
    Zk(ZkResolver),
}

#[async_trait]
#[enum_dispatch(ConfigResolver)]
pub trait Resolver {
    // Check if resolver can be restored from error
    fn is_failable(&self) -> bool {
        false
    }
    // Check if resolver can be repeatedly used
    fn is_repeatable(&self) -> bool {
        false
    }
    //
    async fn bootstrap(&mut self) -> Result<(), AgentError> {
        Ok(())
    }
    //
    fn get_reader(&self) -> Result<ConfigReader, AgentError>;
    // Apply collected config
    fn apply(&mut self, _config: &ZkConfig) -> Result<(), AgentError> {
        Ok(())
    }
    // Wait for next round
    async fn sleep(&self, _status: bool) {}
}

impl TryFrom<CliArgs> for ConfigResolver {
    type Error = AgentError;

    fn try_from(args: CliArgs) -> Result<ConfigResolver, Self::Error> {
        if args.config.is_some() {
            return Ok(ConfigResolver::File(StaticResolver::try_from(args)?));
        }
        if args.bootstrap_state.is_some() {
            return Ok(ConfigResolver::Zk(ZkResolver::try_from(args)?));
        }
        Err(AgentError::ConfigurationError(
            "Cannot get resolver".to_string(),
        ))
    }
}

// Stub resolver for disabled features
pub struct StubResolver;

impl TryFrom<CliArgs> for StubResolver {
    type Error = AgentError;

    fn try_from(_args: CliArgs) -> Result<StubResolver, Self::Error> {
        Err(AgentError::FeatureDisabledError(
            "Resolver is disabled".to_string(),
        ))
    }
}

impl Resolver for StubResolver {
    fn is_failable(&self) -> bool {
        false
    }
    fn is_repeatable(&self) -> bool {
        false
    }
    fn get_reader(&self) -> Result<ConfigReader, AgentError> {
        Err(AgentError::FeatureDisabledError(
            "Resolver is disabled".into(),
        ))
    }
}
