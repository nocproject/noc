// ---------------------------------------------------------------------
// test collector implementation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use super::super::{Collectable, Collector, NoConfig, Status};
use super::TestOut;
use crate::error::AgentError;
use async_trait::async_trait;

pub struct ConfigStub;
pub type TestCollector = Collector<NoConfig<ConfigStub>>;

#[async_trait]
impl Collectable for TestCollector {
    const NAME: &'static str = "test";
    type Output = TestOut;
    async fn collect(&self) -> Result<Status, AgentError> {
        Ok(Status::Ok)
    }
}
