// ---------------------------------------------------------------------
// TWAMP Request-TW-Session
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::{NTPTimeStamp, UTCDateTime, CMD_REQUEST_TW_SESSION, MBZ};
use crate::proto::frame::{FrameError, FrameReader, FrameWriter};
use bytes::{Buf, BufMut, BytesMut};

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
/// |                         MBZ (8 octets)                        |
/// |                                                               |
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
/// NB:
/// Test session utilizes same addresses as the control one. So following fields are ignored:
/// Sender port, Sender address, Receiver port, Receiver address.
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct RequestTWSession {
    pub ipvn: u8,
    // Test session utilizes same addresses as the control one
    // Ignored
    // sender_port: u16,
    // receiver_port: u16,
    // sender_address: Bytes,
    // receiver_address: Bytes,
    pub padding_length: u32,
    pub start_time: UTCDateTime,
    pub timeout: u64,
    pub type_p: u32,
    // hmac: bytes,
}

impl FrameReader for RequestTWSession {
    fn min_size() -> usize {
        112
    }
    fn parse(s: &mut BytesMut) -> Result<RequestTWSession, FrameError> {
        // Command, 1 octet
        let cmd = s.get_u8();
        if cmd != CMD_REQUEST_TW_SESSION {
            return Err(FrameError);
        }
        // MBZ 4 bits + IPVN 4 bits
        let ipvn = s.get_u8();
        if ipvn != 4 && ipvn != 6 {
            return Err(FrameError);
        }
        // Conf-Sender, 2 octets, must be zero
        let conf_sender = s.get_u8();
        if conf_sender != 0 {
            return Err(FrameError);
        }
        // Conf-Receiver, 2 octets, must be zero
        let conf_receiver = s.get_u8();
        if conf_receiver != 0 {
            return Err(FrameError);
        }
        // Number of Schedule Slots, 4 octets, must be zero
        let num_slots = s.get_u32();
        if num_slots != 0 {
            return Err(FrameError);
        }
        // Number of Packets, 4 octets, must be zero
        let num_packets = s.get_u32();
        if num_packets != 0 {
            return Err(FrameError);
        }
        // Sender and Receiver ports and addresses are ignored
        // Session identifier is ignored
        s.advance(36 + 16);
        // Padding length, 4 octets
        let padding_length = s.get_u32();
        // Start-Time, 8 octets
        let ts = NTPTimeStamp::new(s.get_u32(), s.get_u32());
        // Timeout, 8 octets
        let timeout = s.get_u64();
        // Type-P, 4 octets
        let type_p = s.get_u32();
        // MBZ 8 octets
        s.advance(8);
        // HMAC 16 octets
        s.advance(16);
        Ok(RequestTWSession {
            ipvn,
            padding_length,
            start_time: ts.into(),
            timeout,
            type_p,
        })
    }
}

impl FrameWriter for RequestTWSession {
    /// Get size of serialized frame
    fn size(&self) -> usize {
        112
    }
    /// Serialize frame to buffer
    fn write_bytes(&self, s: &mut BytesMut) -> Result<(), FrameError> {
        // Command, 1 octet
        s.put_u8(CMD_REQUEST_TW_SESSION);
        // MBZ 4 bits + IPVN 4 bits
        s.put_u8(self.ipvn);
        // Conf-Sender, 1 octets and Conf-Receiver, 1 octets, both zero
        s.put_u16(0);
        // Number of schedule slots, 4 octets, set to zero
        s.put_u32(0);
        // Number of packets, 4 octets, set to zero
        s.put_u32(0);
        // Sender Port, Receiver Port, Sender Address, Receiver Address
        // 36 octets, set to zero
        s.put(&MBZ[..36]);
        // Session id, 16 octets, set to zero
        s.put(&MBZ[..16]);
        // Padding length, 4 octets
        s.put_u32(self.padding_length);
        // Start time, 8 octets
        let ts: NTPTimeStamp = self.start_time.into();
        s.put_u32(ts.secs());
        s.put_u32(ts.fracs());
        // Timeout, 8 octets
        s.put_u64(self.timeout);
        // Type-P, 4 octets
        s.put_u32(self.type_p);
        // MBZ, 8 octets
        s.put(&MBZ[..8]);
        // HMAC, 16 octets
        s.put(&MBZ[..16]);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::RequestTWSession;
    use crate::proto::frame::{FrameReader, FrameWriter};
    use bytes::{Buf, BytesMut};
    use chrono::{TimeZone, Utc};

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
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // MBZ, 8 octets
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, // HMAC, 16 octets
    ];

    fn get_request_tw_session() -> RequestTWSession {
        RequestTWSession {
            ipvn: 4,
            padding_length: 0,
            start_time: Utc.ymd(2021, 2, 12).and_hms(10, 0, 0),
            timeout: 255,
            type_p: 46,
        }
    }

    #[test]
    fn test_request_tw_session_min_size() {
        assert_eq!(RequestTWSession::min_size(), 112);
    }

    #[test]
    fn test_request_tw_session_parse() {
        let mut buf = BytesMut::from(REQUEST_TW_SESSION1);
        let expected = get_request_tw_session();
        let res = RequestTWSession::parse(&mut buf);
        assert_eq!(buf.remaining(), 0);
        assert_eq!(res, Ok(expected))
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
