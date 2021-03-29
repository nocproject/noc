// ---------------------------------------------------------------------
// Packet models base class
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use enum_dispatch::enum_dispatch;

/// Packet for modeling
#[derive(Debug, PartialEq)]
pub struct Packet {
    pub seq: usize,
    pub size: usize,
    pub next_ns: u64,
}

// Nanosecond
pub const NS: u64 = 1_000_000_000;

#[enum_dispatch(PacketModels)]
pub trait GetPacket {
    fn get_packet(self, seq: usize) -> Packet;
}
