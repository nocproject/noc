// ---------------------------------------------------------------------
// TWAMP Protocol Frames
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

/// RFC-5357, A Two-Way Active Measurement Protocol (TWAMP)

pub const MODE_REFUSED: u32 = 0;
pub const MODE_UNAUTHENTICATED: u32 = 1;
pub const MODE_AUTHENTICATED: u32 = 2;
pub const MODE_ENCRYPTED: u32 = 4;

pub const DEFAULT_COUNT: u32 = 1024;

pub const CMD_START_SESSIONS: u8 = 2;
pub const CMD_STOP_SESSIONS: u8 = 3;
pub const CMD_REQUEST_TW_SESSION: u8 = 5;

// Accept values
pub const ACCEPT_OK: u8 = 0;
pub const ACCEPT_FAILURE: u8 = 1; // Failure, reason unspecified (catch-all).
pub const ACCEPT_INTERNAL_ERROR: u8 = 2;
pub const ACCEPT_PARTIAL_UNSUPPORTED: u8 = 3; // Some aspect of request is not supported.
pub const ACCEPT_PERMANENT_FAILURE: u8 = 4; // Permanent failure
pub const ACCEPT_TEMP_FAILURE: u8 = 5; // Temporal failure

static MBZ: &[u8] = &[
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
];

mod accept_session;
mod ntp;
mod request_tw_session;
mod server_greeting;
mod server_start;
mod setup_response;
mod start_ack;
mod start_sessions;
mod stop_sessions;
mod test_request;
mod test_response;

pub use accept_session::AcceptSession;
pub use ntp::{NTPTimeStamp, UTCDateTime};
pub use request_tw_session::RequestTWSession;
pub use server_greeting::ServerGreeting;
pub use server_start::ServerStart;
pub use setup_response::SetupResponse;
pub use start_ack::StartAck;
pub use start_sessions::StartSessions;
pub use stop_sessions::StopSessions;
pub use test_request::TestRequest;
pub use test_response::TestResponse;
