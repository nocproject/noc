// ---------------------------------------------------------------------
// test collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::collectors::base::{Collectable, Collector, Status};
use crate::zk::Configurable;
use async_trait::async_trait;
use serde::Deserialize;
use std::error::Error;

#[derive(Deserialize)]
pub struct TestConfig {}

impl Configurable<TestConfig> for TestConfig {}

pub type TestCollector = Collector<TestConfig>;

#[async_trait]
impl Collectable for TestCollector {
    async fn collect(&self) -> Result<Status, Box<dyn Error>> {
        Ok(Status::Ok)
    }
}
