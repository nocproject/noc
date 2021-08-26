// ---------------------------------------------------------------------
// Modbus data
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use serde::Deserialize;
use std::hash::Hash;

#[derive(Deserialize, Debug, Clone, Copy, Hash)]
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
    #[serde(rename = "f32_be")]
    F32Be,
    #[serde(rename = "f32_le")]
    F32Le,
    #[serde(rename = "f32_bs")]
    F32Bs,
    #[serde(rename = "f32_ls")]
    F32Ls,
}

impl ModbusFormat {
    pub fn modbus_try_from(self, v: Vec<u16>) -> Result<f64, AgentError> {
        match self {
            ModbusFormat::I16Be => Ok(ModbusFormat::read_16be(v)? as i16 as f64),
            ModbusFormat::U16Be => Ok(ModbusFormat::read_16be(v)? as f64),
            ModbusFormat::I32Be => Ok(ModbusFormat::read_32be(v)? as i32 as f64),
            ModbusFormat::I32Le => Ok(ModbusFormat::read_32le(v)? as i32 as f64),
            ModbusFormat::I32Bs => Ok(ModbusFormat::read_32bs(v)? as i32 as f64),
            ModbusFormat::I32Ls => Ok(ModbusFormat::read_32ls(v)? as i32 as f64),
            ModbusFormat::U32Be => Ok(ModbusFormat::read_32be(v)? as f64),
            ModbusFormat::U32Le => Ok(ModbusFormat::read_32le(v)? as f64),
            ModbusFormat::U32Bs => Ok(ModbusFormat::read_32bs(v)? as f64),
            ModbusFormat::U32Ls => Ok(ModbusFormat::read_32ls(v)? as f64),
            ModbusFormat::F32Be => Ok(f32::from_bits(ModbusFormat::read_32be(v)?) as f64),
            ModbusFormat::F32Le => Ok(f32::from_bits(ModbusFormat::read_32le(v)?) as f64),
            ModbusFormat::F32Bs => Ok(f32::from_bits(ModbusFormat::read_32bs(v)?) as f64),
            ModbusFormat::F32Ls => Ok(f32::from_bits(ModbusFormat::read_32ls(v)?) as f64),
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
            ModbusFormat::F32Be => 2,
            ModbusFormat::F32Le => 2,
            ModbusFormat::F32Bs => 2,
            ModbusFormat::F32Ls => 2,
        }
    }
    // Layouts
    fn read_16be(v: Vec<u16>) -> Result<u16, AgentError> {
        if v.is_empty() {
            return Err(AgentError::ParseError("empty data".to_string()));
        }
        Ok(v[0])
    }
    fn read_32be(v: Vec<u16>) -> Result<u32, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        Ok(((v[0] as u32) << 16) + v[1] as u32)
    }
    fn read_32le(v: Vec<u16>) -> Result<u32, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = (v[1] & 0xff) as u32;
        let o2 = ((v[1] >> 8) & 0xff) as u32;
        let o3 = (v[0] & 0xff) as u32;
        let o4 = ((v[0] >> 8) & 0xff) as u32;
        Ok((o1 << 24) + (o2 << 16) + (o3 << 8) + o4)
    }
    fn read_32bs(v: Vec<u16>) -> Result<u32, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = (v[0] & 0xff) as u32;
        let o2 = ((v[0] >> 8) & 0xff) as u32;
        let o3 = (v[1] & 0xff) as u32;
        let o4 = ((v[1] >> 8) & 0xff) as u32;
        Ok((o1 << 24) + (o2 << 16) + (o3 << 8) + o4)
    }
    fn read_32ls(v: Vec<u16>) -> Result<u32, AgentError> {
        if v.len() < 2 {
            return Err(AgentError::ParseError("short data".to_string()));
        }
        let o1 = ((v[1] >> 8) & 0xff) as u32;
        let o2 = (v[1] & 0xff) as u32;
        let o3 = ((v[0] >> 8) & 0xff) as u32;
        let o4 = (v[0] & 0xff) as u32;
        Ok((o1 << 24) + (o2 << 16) + (o3 << 8) + o4)
    }
}

#[cfg(test)]
mod tests {
    use super::ModbusFormat;
    use assert_approx_eq::assert_approx_eq;
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
    #[test]
    fn test_f32_be_1() {
        let data = [0x3fu8, 0x80u8, 0x37u8, 0x4du8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::F32Be.modbus_try_from(msg).unwrap();
        assert_approx_eq!(result, 1.0016876, 1e-6);
    }
    #[test]
    fn test_f32_le_1() {
        let data = [0x4du8, 0x37u8, 0x80u8, 0x3fu8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::F32Le.modbus_try_from(msg).unwrap();
        assert_approx_eq!(result, 1.0016876, 1e-6);
    }
    #[test]
    fn test_f32_bs_1() {
        let data = [0x80u8, 0x3fu8, 0x4du8, 0x37u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::F32Bs.modbus_try_from(msg).unwrap();
        assert_approx_eq!(result, 1.0016876, 1e-6);
    }
    #[test]
    fn test_f32_ls_1() {
        let data = [0x37u8, 0x4du8, 0x3fu8, 0x80u8];
        let msg = into_vec16(&data);
        let result = ModbusFormat::F32Ls.modbus_try_from(msg).unwrap();
        assert_approx_eq!(result, 1.0016876, 1e-6);
    }
}
