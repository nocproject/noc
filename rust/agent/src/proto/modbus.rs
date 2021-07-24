// ---------------------------------------------------------------------
// Modbus data
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Deserialize;

#[derive(Deserialize, Debug, Clone, Copy)]
pub enum ModbusFormat {
    // 16 bit
    #[serde(rename = "i16_be")]
    I16Be,
    #[serde(rename = "u16_be")]
    U16Be,
    // 32 bit
    #[serde(rename = "i32_be")]
    I32Be,
    #[serde(rename = "i32_le")]
    I32Le,
    #[serde(rename = "i32_bs")]
    I32Bs,
    #[serde(rename = "i32_ls")]
    I32Ls,
    #[serde(rename = "u32_be")]
    U32Be,
    #[serde(rename = "u32_le")]
    U32Le,
    #[serde(rename = "u32_bs")]
    U32Bs,
    #[serde(rename = "u32_ls")]
    U32Ls,
}

impl ModbusFormat {
    pub fn modbus_try_from(self, v: Vec<u16>) -> Result<f64, AgentError> {
        match self {
            ModbusFormat::I16Be => ModbusFormat::from_i16_be(v),
            ModbusFormat::U16Be => ModbusFormat::from_u16_be(v),
            ModbusFormat::I32Be => ModbusFormat::from_i32_be(v),
            ModbusFormat::I32Le => ModbusFormat::from_i32_le(v),
            ModbusFormat::I32Bs => ModbusFormat::from_i32_bs(v),
            ModbusFormat::I32Ls => ModbusFormat::from_i32_ls(v),
            ModbusFormat::U32Be => ModbusFormat::from_u32_be(v),
            ModbusFormat::U32Le => ModbusFormat::from_u32_le(v),
            ModbusFormat::U32Bs => ModbusFormat::from_u32_bs(v),
            ModbusFormat::U32Ls => ModbusFormat::from_u32_ls(v),
        }
    }
    pub fn min_count(self) -> u16 {
        match self {
            ModbusFormat::I16Be => 1,
            ModbusFormat::U16Be => 1,
            ModbusFormat::I32Be => 2,
            ModbusFormat::I32Le => 2,
            ModbusFormat::I32Bs => 2,
            ModbusFormat::I32Ls => 2,
            ModbusFormat::U32Be => 2,
            ModbusFormat::U32Le => 2,
            ModbusFormat::U32Bs => 2,
            ModbusFormat::U32Ls => 2,
        }
    }
    fn from_i16_be(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.is_empty() {
            return Err(AgentError::ParseError("empty data".to_string()));
        }
        Ok(v[0] as i16 as f64)
    }
    fn from_u16_be(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.is_empty() {
            return Err(AgentError::ParseError("empty data".to_string()));
        }
        Ok(v[0] as f64)
    }
    fn from_i32_be(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        Ok(((((v[0] as u32) << 16) + v[1] as u32) as i32) as f64)
    }
    fn from_i32_le(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = (v[1] & 0xff) as u32;
        let o2 = ((v[1] >> 8) & 0xff) as u32;
        let o3 = (v[0] & 0xff) as u32;
        let o4 = ((v[0] >> 8) & 0xff) as u32;
        let r = (o1 << 24) + (o2 << 16) + (o3 << 8) + o4;
        Ok((r as i32) as f64)
    }
    fn from_i32_bs(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = (v[0] & 0xff) as u32;
        let o2 = ((v[0] >> 8) & 0xff) as u32;
        let o3 = (v[1] & 0xff) as u32;
        let o4 = ((v[1] >> 8) & 0xff) as u32;
        let r = (o1 << 24) + (o2 << 16) + (o3 << 8) + o4;
        Ok((r as i32) as f64)
    }
    fn from_i32_ls(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = ((v[1] >> 8) & 0xff) as u32;
        let o2 = (v[1] & 0xff) as u32;
        let o3 = ((v[0] >> 8) & 0xff) as u32;
        let o4 = (v[0] & 0xff) as u32;
        let r = (o1 << 24) + (o2 << 16) + (o3 << 8) + o4;
        Ok((r as i32) as f64)
    }
    fn from_u32_be(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        Ok((((v[0] as u32) << 16) + v[1] as u32) as f64)
    }
    fn from_u32_le(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = (v[1] & 0xff) as u32;
        let o2 = ((v[1] >> 8) & 0xff) as u32;
        let o3 = (v[0] & 0xff) as u32;
        let o4 = ((v[0] >> 8) & 0xff) as u32;
        let r = (o1 << 24) + (o2 << 16) + (o3 << 8) + o4;
        Ok(r as f64)
    }
    fn from_u32_bs(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = (v[0] & 0xff) as u32;
        let o2 = ((v[0] >> 8) & 0xff) as u32;
        let o3 = (v[1] & 0xff) as u32;
        let o4 = ((v[1] >> 8) & 0xff) as u32;
        let r = (o1 << 24) + (o2 << 16) + (o3 << 8) + o4;
        Ok(r as f64)
    }
    fn from_u32_ls(v: Vec<u16>) -> Result<f64, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = ((v[1] >> 8) & 0xff) as u32;
        let o2 = (v[1] & 0xff) as u32;
        let o3 = ((v[0] >> 8) & 0xff) as u32;
        let o4 = (v[0] & 0xff) as u32;
        let r = (o1 << 24) + (o2 << 16) + (o3 << 8) + o4;
        Ok(r as f64)
    }
}

#[cfg(test)]
mod tests {
    use super::ModbusFormat;
    use std::iter::FromIterator;

    // Convert vec of u8 to modbus-style vec of registers
    fn into_vec16(data: &[u8]) -> Vec<u16> {
        Vec::from_iter(
            data.chunks(2)
                .map(|chunk| ((chunk[0] as u16) << 8) + (chunk[1] as u16)),
        )
    }

    #[test]
    fn test_into_vec16_1() {
        let data = [1u8, 2u8];
        let exp = [0x0102u16];
        assert_eq!(into_vec16(&data), Vec::from(&exp[..]));
    }

    #[test]
    fn test_into_vec16_2() {
        let data = [1u8, 2u8, 3u8, 4u8];
        let exp = [0x0102u16, 0x0304u16];
        assert_eq!(into_vec16(&data), Vec::from(&exp[..]));
    }

    #[test]
    fn test_i16_be_1() {
        let data = [1u8, 2u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I16Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, 258.0);
    }

    #[test]
    fn test_i16_be_2() {
        let data = [0xffu8, 1u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I16Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, -255.0);
    }

    #[test]
    fn test_u16_be_1() {
        let data = [1u8, 2u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U16Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, 258.0);
    }

    #[test]
    fn test_u16_be_2() {
        let data = [0xffu8, 1u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U16Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, 65281.0);
    }
    #[test]
    fn test_i32_be_1() {
        let data = [1u8, 2u8, 3u8, 4u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_i32_be_2() {
        let data = [0xffu8, 0xfeu8, 0xfdu8, 0xfcu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, -66052.0);
    }
    #[test]
    fn test_i32_le_1() {
        let data = [4u8, 3u8, 2u8, 1u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Le.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_i32_le_2() {
        let data = [0xfcu8, 0xfdu8, 0xfeu8, 0xffu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Le.modbus_try_from(msg).unwrap();
        assert_eq!(result, -66052.0);
    }
    #[test]
    fn test_i32_bs_1() {
        let data = [2u8, 1u8, 4u8, 3u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Bs.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_i32_bs_2() {
        let data = [0xfeu8, 0xffu8, 0xfcu8, 0xfdu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Bs.modbus_try_from(msg).unwrap();
        assert_eq!(result, -66052.0);
    }
    #[test]
    fn test_i32_ls_1() {
        let data = [3u8, 4u8, 1u8, 2u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Ls.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_i32_ls_2() {
        let data = [0xfdu8, 0xfcu8, 0xffu8, 0xfeu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::I32Ls.modbus_try_from(msg).unwrap();
        assert_eq!(result, -66052.0);
    }
    #[test]
    fn test_u32_be_1() {
        let data = [1u8, 2u8, 3u8, 4u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_u32_be_2() {
        let data = [0xffu8, 0xfeu8, 0xfdu8, 0xfcu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Be.modbus_try_from(msg).unwrap();
        assert_eq!(result, 4294901244.0);
    }
    #[test]
    fn test_u32_le_1() {
        let data = [4u8, 3u8, 2u8, 1u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Le.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_u32_le_2() {
        let data = [0xfcu8, 0xfdu8, 0xfeu8, 0xffu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Le.modbus_try_from(msg).unwrap();
        assert_eq!(result, 4294901244.0);
    }
    #[test]
    fn test_u32_bs_1() {
        let data = [2u8, 1u8, 4u8, 3u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Bs.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_u32_bs_2() {
        let data = [0xfeu8, 0xffu8, 0xfcu8, 0xfdu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Bs.modbus_try_from(msg).unwrap();
        assert_eq!(result, 4294901244.0);
    }
    #[test]
    fn test_u32_ls_1() {
        let data = [3u8, 4u8, 1u8, 2u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Ls.modbus_try_from(msg).unwrap();
        assert_eq!(result, 16909060.0);
    }

    #[test]
    fn test_u32_ls_2() {
        let data = [0xfdu8, 0xfcu8, 0xffu8, 0xfeu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::U32Ls.modbus_try_from(msg).unwrap();
        assert_eq!(result, 4294901244.0);
    }
}
