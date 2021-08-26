// ---------------------------------------------------------------------
// network collector configuration
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use serde::Deserialize;
use std::hash::Hash;

#[derive(Deserialize, Debug, Clone, Hash)]
pub struct NetworkConfig {}
