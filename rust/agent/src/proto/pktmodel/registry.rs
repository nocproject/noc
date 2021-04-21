// ---------------------------------------------------------------------
// Packet Model Registry
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

pub use super::{
    CbrModel, CbrModelConfig, G711Model, G711ModelConfig, G729Model, G729ModelConfig, GetPacket,
    ImixModel, ImixModelConfig, Packet,
};
use crate::error::AgentError;
use enum_dispatch::enum_dispatch;
use serde::Deserialize;
use std::convert::TryFrom;

#[derive(Deserialize, Debug, Clone)]
#[serde(rename_all = "lowercase")]
#[serde(tag = "model")]
pub enum ModelConfig {
    G711(G711ModelConfig),
    G729(G729ModelConfig),
    Cbr(CbrModelConfig),
    Imix(ImixModelConfig),
}

#[enum_dispatch]
#[derive(Debug, Copy, Clone)]
pub enum PacketModels {
    G711(G711Model),
    G729(G729Model),
    Cbr(CbrModel),
    Imix(ImixModel),
}

impl TryFrom<ModelConfig> for PacketModels {
    type Error = AgentError;

    fn try_from(value: ModelConfig) -> Result<Self, Self::Error> {
        Ok(match value {
            ModelConfig::G711(c) => PacketModels::G711(G711Model::try_from(c)?),
            ModelConfig::G729(c) => PacketModels::G729(G729Model::try_from(c)?),
            ModelConfig::Cbr(c) => PacketModels::Cbr(CbrModel::try_from(c)?),
            ModelConfig::Imix(c) => PacketModels::Imix(ImixModel::try_from(c)?),
        })
    }
}
