// ---------------------------------------------------------------------
// IMix packet model
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
pub struct ImixModelConfig {
    #[serde(rename = "model_bandwidth")]
    pub bandwidth: usize,
}

#[derive(Debug, Copy, Clone)]
pub struct ImixModel {
    next_ns: u64,
}

impl TryFrom<ImixModelConfig> for ImixModel {
    type Error = AgentError;

    fn try_from(value: ImixModelConfig) -> Result<Self, Self::Error> {
        Ok(Self {
            next_ns: NS * IMIX_ROUND / (value.bandwidth * IMIX_SAMPLE_COUNT) as u64,
        })
    }
}

impl GetPacket for ImixModel {
    fn get_packet(self, seq: usize) -> Packet {
        Packet {
            seq,
            size: IMIX_SAMPLE[seq % IMIX_SAMPLE_COUNT],
            next_ns: self.next_ns,
        }
    }
}

/// IMIX iterator.
/// Simple IMIX model consists of 7 packets of 64 octets, 4 of 576 and one for 1500.
/// As TWAMP-Response is 20+8+41, pad small packets to 70 octets.  
const IMIX1: usize = 70;
const IMIX1_COUNT: usize = 7;
const IMIX2: usize = 576;
const IMIX2_COUNT: usize = 4;
const IMIX3: usize = 1500;
const IMIX3_COUNT: usize = 1;
const IMIX_SAMPLE_COUNT: usize = IMIX1_COUNT + IMIX2_COUNT + IMIX3_COUNT;
static IMIX_SAMPLE: &[usize; 12] = &[
    IMIX1, IMIX2, IMIX1, IMIX2, IMIX1, IMIX2, IMIX1, IMIX2, IMIX1, IMIX1, IMIX1, IMIX3,
];
const IMIX_ROUND: u64 =
    ((IMIX1_COUNT * IMIX1 + IMIX2_COUNT * IMIX2 + IMIX3_COUNT * IMIX3) * 8) as u64;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::proto::pktmodel::{GetPacket, ModelConfig, PacketModels};

    #[test]
    fn test_imix_model() {
        let model = PacketModels::try_from(ModelConfig::Imix(ImixModelConfig {
            bandwidth: 12_252_000,
        }))
        .unwrap();
        for seq in 0..IMIX_SAMPLE_COUNT {
            let pkt = model.get_packet(seq);
            let expected = Packet {
                seq,
                size: IMIX_SAMPLE[seq % IMIX_SAMPLE_COUNT],
                next_ns: 233_648,
            };
            assert_eq!(pkt, expected);
        }
    }
}
