// ---------------------------------------------------------------------
// Config Parser
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

pub mod base;
pub mod json;

pub use base::{ConfigParser, Parser};
pub use json::JsonParser;
