// ---------------------------------------------------------------------
// TWAMP Request-TW-Session
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{NtpTimeStamp, UtcDateTime, CMD_REQUEST_TW_SESSION, MBZ};
use crate::error::AgentError;
use crate::proto::frame::{FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};
use std::cmp::{Eq, PartialEq};
use std::net::IpAddr;

#[derive(Debug, Clone, Eq, PartialEq)]
pub enum IpVn {
    V4,
    V6,
}

/// ## Request-TW-Session structure
/// RFC-5357: 3.6
/// ```text
///  0                   1                   2                   3
///  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |      5        |  MBZ  | IPVN  |  Conf-Sender  | Conf-Receiver |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                  Number of Schedule Slots                     |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                      Number of Packets                        |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |          Sender Port          |         Receiver Port         |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                        Sender Address                         |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |           Sender Address (cont.) or MBZ (12 octets)           |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                        Receiver Address                       |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |           Receiver Address (cont.) or MBZ (12 octets)         |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                        SID (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                         Padding Length                        |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                           Start Time                          |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                       Timeout, (8 octets)                     |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                       Type-P Descriptor                       |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |     Octets to be reflected    |  Length of padding to reflect |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                       MBZ (4 octets)                          |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// |                                                               |
/// |                       HMAC (16 octets)                        |
/// |                                                               |
/// |                                                               |
/// +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/// ```
/// For TWAMP:
/// * Command number is 5
/// * Conf-Sender and Conf-Receiver both set to 0
/// * Number of Schedule Slots must be set to zero
/// * Number of packets must be set to zero
/// * SID must be set to zeroes
/// RFC-6038 defines additional fields:
/// * Octets to be reflected
/// * Length of padding to reflect
/// NB:
/// Test session utilizes same addresses as the control one. So following fields are ignored, though filled:
/// Sender port, Sender address, Receiver port, Receiver address.
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct RequestTwSession {
    pub ipvn: IpVn,
    // Test session utilizes same addresses as the control one
    // Ignored
    pub sender_port: u16,
    pub receiver_port: u16,
    pub sender_address: IpAddr,
    pub receiver_address: IpAddr,
    pub padding_length: u32,
    pub start_time: UtcDateTime,
    pub timeout: u64,
    pub type_p: u32,
    pub octets_reflected: u16,
    pub reflect_padding: u16,
    // hmac: bytes,
}

impl FrameReader for RequestTwSession {
    fn min_size() -> usize {
        112
    }
    fn parse(s: &mut BytesMut) -> Result<RequestTwSession, AgentError> {
        // Command, 1 octet
        let cmd = s.get_u8();
        if cmd != CMD_REQUEST_TW_SESSION {
            return Err(AgentError::FrameError("Invalid command code".into()));
        }
        // MBZ 4 bits + IPVN 4 bits
        let ipvn = match s.get_u8() {
            4 => IpVn::V4,
            6 => IpVn::V6,
            _ => return Err(AgentError::FrameError("Invalid IP version".into())),
        };
        // Conf-Sender, 2 octets, must be zero
        let conf_sender = s.get_u8();
        if conf_sender != 0 {
            return Err(AgentError::FrameError("Conf-Sender must be zero".into()));
        }
        // Conf-Receiver, 2 octets, must be zero
        let conf_receiver = s.get_u8();
        if conf_receiver != 0 {
            return Err(AgentError::FrameError("Conf-Receiver must be zero".into()));
        }
        // Number of Schedule Slots, 4 octets, must be zero
        let num_slots = s.get_u32();
        if num_slots != 0 {
            return Err(AgentError::FrameError("Num-Slots must be zero".into()));
        }
        // Number of Packets, 4 octets, must be zero
        let num_packets = s.get_u32();
        if num_packets != 0 {
            return Err(AgentError::FrameError("Num-Packets must be zero".into()));
        }
        // Sender Port (2 octets)
        let sender_port = s.get_u16();
        // Receiver Port (2 octets)
        let receiver_port = s.get_u16();
        // Sender address
        let sender_address = match &ipvn {
            IpVn::V4 => {
                let mut sa = [0u8; 4];
                s.copy_to_bytes(4).copy_to_slice(&mut sa);
                s.advance(12); // Skip zeroes
                IpAddr::from(sa)
            }
            IpVn::V6 => {
                let mut sa = [0u8; 16];
                s.copy_to_bytes(4).copy_to_slice(&mut sa);
                IpAddr::from(sa)
            }
        };
        // Sender address
        let receiver_address = match &ipvn {
            IpVn::V4 => {
                let mut da = [0u8; 4];
                s.copy_to_bytes(4).copy_to_slice(&mut da);
                s.advance(12); // Skip zeroes
                IpAddr::from(da)
            }
            IpVn::V6 => {
                let mut da = [0u8; 16];
                s.copy_to_bytes(4).copy_to_slice(&mut da);
                IpAddr::from(da)
            }
        };
        // Session identifier is ignored
        s.advance(16);
        // Padding length, 4 octets
        let padding_length = s.get_u32();
        // Start-Time, 8 octets
        let ts = NtpTimeStamp::new(s.get_u32(), s.get_u32());
        // Timeout, 8 octets
        let timeout = s.get_u64();
        // Type-P, 4 octets
        let type_p = s.get_u32();
        // Octets reflected
        let octets_reflected = s.get_u16();
        // Padding to reflect
        let reflect_padding = s.get_u16();
        // MBZ 4 octets
        s.advance(4);
        // HMAC 16 octets
        s.advance(16);
        Ok(RequestTwSession {
            ipvn,
            sender_port,
            receiver_port,
            sender_address,
            receiver_address,
            padding_length,
            start_time: ts.into(),
            timeout,
            type_p,
            octets_reflected,
            reflect_padding,
        })
    }
}

impl FrameWriter for RequestTwSession {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        112
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), AgentError> {
        // Command, 1 octet
        s.put_u8(CMD_REQUEST_TW_SESSION);
        // MBZ 4 bits + IPVN 4 bits
        match &self.ipvn {
            IpVn::V4 => s.put_u8(4),
            IpVn::V6 => s.put_u8(6),
        }
        // Conf-Sender, 1 octets and Conf-Receiver, 1 octets, both zero
        s.put_u16(0);
        // Number of schedule slots, 4 octets, set to zero
        s.put_u32(0);
        // Number of packets, 4 octets, set to zero
        s.put_u32(0);
        // Sender port, 2 octets
        s.put_u16(self.sender_port);
        // Receiver port, 2 octets
        s.put_u16(self.receiver_port);
        // Sender address, 16 octets
        match (&self.ipvn, self.sender_address) {
            (IpVn::V4, IpAddr::V4(x)) => {
                s.put(&x.octets()[..4]);
                s.put(&MBZ[..12]);
            }
            (IpVn::V6, IpAddr::V6(x)) => s.put(&x.octets()[..16]),
            _ => return Err(AgentError::InternalError("invalid sender address".into())),
        };
        // Receiver address, 16 octets
        match (&self.ipvn, self.receiver_address) {
            (IpVn::V4, IpAddr::V4(x)) => {
                s.put(&x.octets()[..4]);
                s.put(&MBZ[..12]);
            }
            (IpVn::V6, IpAddr::V6(x)) => s.put(&x.octets()[..16]),
            _ => return Err(AgentError::InternalError("invalid receiver address".into())),
        };
        // Session id, 16 octets, set to zero
        s.put(&MBZ[..16]);
        // Padding length, 4 octets
        s.put_u32(self.padding_length);
        // Start time, 8 octets
        let ts: NtpTimeStamp = self.start_time.into();
        s.put_u32(ts.secs());
        s.put_u32(ts.fracs());
        // Timeout, 8 octets
        s.put_u64(self.timeout);
        // Type-P, 4 octets
        s.put_u32(self.type_p);
        // Octets reflected
        s.put_u16(self.octets_reflected);
        // Reflect padding
        s.put_u16(self.reflect_padding);
        // MBZ, 4 octets
        s.put(&MBZ[..4]);
        // HMAC, 16 octets
        s.put(&MBZ[..16]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::{IpVn, RequestTwSession};
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};
    use chrono::{TimeZone, Utc};
    use std::net::{IpAddr, Ipv4Addr};

    static REQUEST_TW_SESSION1: &[u8] = &[
        0x05, // Command, 5
        0x04, // IPVN 4
        0x00, // Conf-Sender
        0x00, // Conf-Receiver
        0x00, 0x00, 0x00, 0x00, // Number of slots
        0x00, 0x00, 0x00, 0x00, // Number of packets
        0x00, 0x00, // Sender Port
        0x00, 0x00, // Receiver Port
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // Sender Address
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // Receiver Address
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // SID
        0x00, 0x00, 0x00, 0x00, // Padding length
        0xe3, 0xd0, 0xd0, 0x20, 0x00, 0x00, 0x00, 0x00, // Start Time, 8 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, // Timeout, 8 octets
        0x00, 0x00, 0x00, 0x2e, // Type-P, DSCP EF (46/0x2e)
        0x00, 0x00, // Octets reflected
        0x00, 0x00, // Padding to reflect
        0x00, 0x00, 0x00, 0x00, // MBZ, 4 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // HMAC, 16 octets
    ];

    fn get_request_tw_session() -> RequestTwSession {
        RequestTwSession {
            ipvn: IpVn::V4,
            sender_port: 0,
            receiver_port: 0,
            sender_address: IpAddr::V4(Ipv4Addr::UNSPECIFIED),
            receiver_address: IpAddr::V4(Ipv4Addr::UNSPECIFIED),
            padding_length: 0,
            start_time: Utc.ymd(2021, 2, 12).and_hms(10, 0, 0),
            timeout: 255,
            type_p: 46,
            octets_reflected: 0,
            reflect_padding: 0,
        }
    }

    #[test]
    fn test_request_tw_session_min_size() {
        assert_eq!(RequestTwSession::min_size(), 112);
    }

    #[test]
    fn test_request_tw_session_parse() {
        let mut buf = BytesMut::from(REQUEST_TW_SESSION1);
        let expected = get_request_tw_session();
        let res = RequestTwSession::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert!(res.is_ok());
        assert_eq!(res.unwrap(), expected);
    }

    #[test]
    fn test_request_tw_session_size() {
        let sg = get_request_tw_session();
        assert_eq!(sg.size(), 112)
    }

    #[test]
    fn test_request_tw_session_write_bytes() {
        let msg = get_request_tw_session();
        let mut buf = BytesMut::with_capacity(msg.size());
        let res = msg.write_bytes(&mut buf);
        assert!(res.is_ok());
        assert_eq!(buf.split(), BytesMut::from(REQUEST_TW_SESSION1));
    }
}
