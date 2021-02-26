// ---------------------------------------------------------------------
// NTP protocol utilities
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------
use chrono::{DateTime, TimeZone, Utc};

#[derive(Debug, PartialEq, Clone, Copy)]
pub struct NTPTimeStamp {
    secs: u32,
    fracs: u32,
}

pub type UTCDateTime = DateTime<Utc>;
const NTP_OFFSET: i64 = 2_208_988_800;
const NTP_SCALE: f64 = 4_294_967_295.0;
const MAX_NANOS: f64 = 1_000_000_000.0;

impl NTPTimeStamp {
    pub fn new(secs: u32, fracs: u32) -> NTPTimeStamp {
        NTPTimeStamp { secs, fracs }
    }
    pub fn secs(&self) -> u32 {
        self.secs
    }
    pub fn fracs(&self) -> u32 {
        self.fracs
    }
}

impl From<UTCDateTime> for NTPTimeStamp {
    fn from(ts: DateTime<Utc>) -> NTPTimeStamp {
        let secs = ts.timestamp();
        let nanos = ts.timestamp_subsec_nanos();
        NTPTimeStamp {
            secs: (secs + NTP_OFFSET) as u32,
            fracs: (nanos as f64 * NTP_SCALE / MAX_NANOS) as u32,
        }
    }
}

impl From<NTPTimeStamp> for UTCDateTime {
    fn from(ts: NTPTimeStamp) -> UTCDateTime {
        Utc.timestamp(
            ts.secs as i64 - NTP_OFFSET,
            (ts.fracs as f64 * MAX_NANOS / NTP_SCALE) as u32,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::{NTPTimeStamp, UTCDateTime};
    use chrono::{Duration, TimeZone, Utc};

    fn get_utc_timestamp() -> UTCDateTime {
        Utc.ymd(2021, 2, 12).and_hms_milli(10, 0, 0, 500)
    }

    fn get_ntp_timestamp() -> NTPTimeStamp {
        NTPTimeStamp::new(3822112800, 2147483647)
    }

    #[test]
    fn test_secs() {
        let ts = get_ntp_timestamp();
        assert_eq!(ts.secs(), 3822112800);
    }
    #[test]
    fn test_fracs() {
        let ts = get_ntp_timestamp();
        assert_eq!(ts.fracs(), 2147483647);
    }
    #[test]
    fn test_from_utc() {
        let utc_ts = get_utc_timestamp();
        let ntp_ts: NTPTimeStamp = utc_ts.into();
        let expected = get_ntp_timestamp();
        assert_eq!(ntp_ts, expected);
    }
    #[test]
    fn test_from_ntp() {
        let ntp_ts = get_ntp_timestamp();
        let utc_ts: UTCDateTime = ntp_ts.into();
        let expected = get_utc_timestamp();
        let delta = utc_ts - expected;
        assert!(delta < Duration::microseconds(1));
    }
}
