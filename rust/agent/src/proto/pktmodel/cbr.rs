// ---------------------------------------------------------------------
// Constant bitrate Packet Model
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{GetPacket, Packet, NS};
use crate::error::AgentError;
use serde::Deserialize;
use std::convert::TryFrom;
use std::hash::Hash;

#[derive(Deserialize, Debug, Clone, Hash)]
pub struct CbrModelConfig {
    #[serde(rename = "model_bandwidth")]
    pub bandwidth: usize,
    #[serde(rename = "model_size")]
    pub size: usize,
}

#[derive(Debug, Copy, Clone)]
pub struct CbrModel {
    size: usize,
    next_ns: u64,
}

impl TryFrom<CbrModelConfig> for CbrModel {
    type Error = AgentError;

    fn try_from(value: CbrModelConfig) -> Result<Self, Self::Error> {
        Ok(Self {
            size: value.size,
            next_ns: NS / (value.bandwidth / (value.size * 8)) as u64,
        })
    }
}

impl GetPacket for CbrModel {
    fn get_packet(self, seq: usize) -> Packet {
        Packet {
            seq,
            size: self.size,
            next_ns: self.next_ns,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::proto::pktmodel::{GetPacket, ModelConfig, PacketModels};

    #[test]
    fn test_cbr_model() {
        let model = PacketModels::try_from(ModelConfig::Cbr(CbrModelConfig {
            bandwidth: 8_000_000,
            size: 100,
        }))
        .unwrap();
        let pkt = model.get_packet(0);
        let expected = Packet {
            seq: 0,
            size: 100,
            next_ns: 100_000,
        };
        assert_eq!(pkt, expected);
    }
}
