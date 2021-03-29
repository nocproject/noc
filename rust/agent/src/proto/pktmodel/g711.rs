// ---------------------------------------------------------------------
// G.711 Packet model
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{GetPacket, Packet, NS};
use serde::Deserialize;
use std::convert::TryFrom;
use std::error::Error;

#[derive(Deserialize, Debug, Clone)]
pub struct G711ModelConfig {}

#[derive(Debug, Copy, Clone)]
pub struct G711Model;

impl TryFrom<G711ModelConfig> for G711Model {
    type Error = Box<dyn Error>;

    fn try_from(_value: G711ModelConfig) -> Result<Self, Self::Error> {
        Ok(Self)
    }
}

impl GetPacket for G711Model {
    fn get_packet(self, seq: usize) -> Packet {
        Packet {
            seq,
            size: 20 + 8 + 12 + 160,
            next_ns: NS / 50,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::proto::pktmodel::{GetPacket, ModelConfig, PacketModels};

    #[test]
    fn test_g711_model() {
        let model = PacketModels::try_from(ModelConfig::G711(G711ModelConfig {})).unwrap();
        let pkt = model.get_packet(0);
        let expected = Packet {
            seq: 0,
            size: 200,
            next_ns: 20_000_000,
        };
        assert_eq!(pkt, expected);
    }
}
