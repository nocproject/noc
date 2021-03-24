// ---------------------------------------------------------------------
// test collector configuration
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Configurable;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct TestConfig {}

impl Configurable for TestConfig {}
