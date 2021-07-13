// ---------------------------------------------------------------------
// Various utilities
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use std::convert::TryFrom;
use std::string::ToString;

pub struct MAC(String);

impl TryFrom<String> for MAC {
    type Error = AgentError;
    fn try_from(value: String) -> Result<Self, Self::Error> {
        let mut cleaned_mac = value;
        while !cleaned_mac.is_empty() && cleaned_mac.ends_with('\n') {
            cleaned_mac.pop();
        }
        // @todo: Detect format of MAC
        let parts = cleaned_mac
            .split(':')
            .map(|v| from_hex(v))
            .collect::<Result<Vec<u8>, AgentError>>()?;
        if parts.len() != 6 {
            return Err(AgentError::ParseError("invalid mac".to_string()));
        }
        Ok(MAC(parts
            .iter()
            .map(|v| format!("{:02X}", v))
            .collect::<Vec<String>>()
            .join(":")))
    }
}

impl ToString for MAC {
    fn to_string(&self) -> String {
        self.0.clone()
    }
}

impl MAC {
    pub fn is_ignored(&self) -> bool {
        self.0.eq("00:00:00:00:00:00")
    }
}

fn from_hex_digit(value: u8) -> Result<u8, AgentError> {
    if (48..=57).contains(&value) {
        return Ok(value - 48);
    }
    if (97..=102).contains(&value) {
        return Ok(value - 97 + 10);
    }
    if (65..=70).contains(&value) {
        return Ok(value as u8 - 65 + 10);
    }
    Err(AgentError::ParseError("parse error".to_string()))
}

pub fn from_hex(value: &str) -> Result<u8, AgentError> {
    match value.len() {
        // Single digit
        1 => from_hex_digit(value.bytes().next().unwrap()),
        // Double digits
        2 => {
            let mut b = value.bytes();
            Ok((from_hex_digit(b.next().unwrap())? << 4) + from_hex_digit(b.next().unwrap())?)
        }
        _ => Err(AgentError::ParseError("parse error".to_string())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_from_hex() {
        for i in 0..255u8 {
            let short_lower_case = format!("{:x}", i);
            assert_eq!(from_hex(&short_lower_case).unwrap(), i);
            let long_lower_case = format!("{:02x}", i);
            assert_eq!(from_hex(&long_lower_case).unwrap(), i);
            let short_upper_case = format!("{:X}", i);
            assert_eq!(from_hex(&short_upper_case).unwrap(), i);
            let long_upper_case = format!("{:02X}", i);
            assert_eq!(from_hex(&long_upper_case).unwrap(), i);
        }
    }

    #[test]
    fn test_mac() {
        assert!(MAC::try_from("0".to_string()).is_err());
        assert!(MAC::try_from("0:1:2".to_string()).is_err());
        assert_eq!(
            MAC::try_from("0:1:2:3:4:05".to_string())
                .unwrap()
                .to_string(),
            "00:01:02:03:04:05"
        );
        assert!(MAC::try_from("0:1:2:3:004:5".to_string()).is_err());
    }
}
