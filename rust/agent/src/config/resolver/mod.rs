// ---------------------------------------------------------------------
// Config resolvers
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

pub mod base;
pub mod r#static;
pub mod zk;

pub use base::{ConfigResolver, Resolver};
pub use r#static::StaticResolver;
pub use zk::ZkResolver;
