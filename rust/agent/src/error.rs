// ---------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use thiserror::Error;
use tokio::time::error::Elapsed;

#[derive(Error, Debug)]
pub enum AgentError {
    // Invalid command line
    #[error("Invalid command line: {0}")]
    CliError(String),
    // Feature is not implemented still
    #[error("Not implemented")]
    NotImplementedError,
    // Failed to bootstrap
    #[error("Bootstrap error: {0}")]
    BootstrapError(String),
    // Generic I/O Error
    #[error(transparent)]
    IoError(#[from] std::io::Error),
    // Network error
    #[error("Network error: {0}")]
    NetworkError(String),
    // Network URL fetching error
    #[error("Fetch error: {0}")]
    FetchError(String),
    // JSON parsing error
    #[error("Parse error: {0}")]
    ParseError(String),
    // Invalid collector configuration
    #[error("Configuration error: {0}")]
    ConfigurationError(String),
    // Packet format error
    #[error("Frame error: {0}")]
    FrameError(String),
    //
    #[error("Timed out")]
    TimeOutError(#[from] Elapsed),
    //
    #[error("Internal error: {0}")]
    InternalError(String),
    // Feature is disabled during compile time
    #[error("Feature {0} is disabled")]
    FeatureDisabledError(String),
    // Serialization error
    #[error("Serialization error: {0}")]
    SerializationError(String),
}
