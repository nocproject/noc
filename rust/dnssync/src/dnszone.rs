/* ---------------------------------------------------------------------
 * DNSZone data structure
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::error::Error;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct DNSZone {
    pub name: String,
    pub serial: String,
    pub masters: Vec<String>,
    pub slaves: Vec<String>,
    pub records: Vec<RR>,
}

#[derive(Debug, Deserialize)]
pub struct RR {
    pub name: String,
    #[serde(rename(deserialize = "type"))]
    pub rr_type: String,
    #[serde(rename(deserialize = "rdata"))]
    pub data: String,
    pub ttl: usize,
    pub priority: Option<usize>,
}

#[derive(Debug, Default)]
pub struct SOA {
    pub primary: String,
    pub contact: String,
    pub serial: String,
    pub refresh: usize,
    pub retry: usize,
    pub expire: usize,
    pub ttl: usize,
}

impl RR {
    pub fn is_txt(&self) -> bool {
        self.rr_type == "TXT"
    }
    pub fn is_cname(&self) -> bool {
        self.rr_type == "CNAME"
    }
}

impl DNSZone {
    pub fn get_soa(&self) -> Result<SOA, Error> {
        let mut soa = SOA::default();
        for (i, v) in self.records[0].data.splitn(7, " ").enumerate() {
            match i {
                0 => soa.primary = v.to_string(),
                1 => soa.contact = v.to_string(),
                2 => soa.serial = v.to_string(),
                3 => soa.refresh = v.parse()?,
                4 => soa.retry = v.parse()?,
                5 => soa.expire = v.parse()?,
                6 => soa.ttl = v.parse()?,
                _ => Err(Error::ParseError(String::from("Extra SOA part")))?,
            }
        }
        Ok(soa)
    }

    pub fn pretty_name(&self) -> Result<String, Error> {
        let (name, result) = idna::domain_to_unicode(&self.name);
        match result {
            Ok(_) => Ok(name),
            Err(_) => Err(Error::PunicodeError),
        }
    }
}
