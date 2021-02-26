/* ---------------------------------------------------------------------
 * Command-line arguments parsing
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use clap::{clap_app, crate_authors, crate_description, crate_version, value_t};
use std::ffi::OsString;

const DEFAULT_ERR_TIMEOUT: u64 = 5;
const DEFAULT_REQUEST_LIMIT: usize = 1000;

#[derive(Debug)]
pub struct CmdArgs {
    pub api_key: String,
    pub noc_url: String,
    pub zones_path: String,
    pub zones_chroot_path: Option<String>,
    pub host: String,
    pub request_limit: usize,
    pub error_timeout: u64,
    pub insecure: bool,
    pub daemon: bool,
    pub dry_run: bool,
    pub verbose: bool,
}

impl CmdArgs {
    pub fn new() -> Self {
        Self::new_from(std::env::args_os().into_iter()).unwrap_or_else(|e| e.exit())
    }

    pub fn new_from<I, T>(args: I) -> Result<Self, clap::Error>
    where
        I: Iterator<Item = T>,
        T: Into<OsString> + Clone,
    {
        return clap_app!(("noc-sync-bind") =>
            (version: crate_version!())
            (author: crate_authors!())
            (about: crate_description!())
            (@arg VERBOSE: -v  --verbose "Verbose logging")
            (@arg API_KEY: -k --("api-key") +takes_value +required env[NOC_API_KEY] "Sets API Key for authentication")
            (@arg NOC_URL: -u --("noc-url") +takes_value +required env[NOC_URL] "Sets NOC installation URL")
            (@arg ZONES_PATH: -z --("zones-path") +takes_value +required env[NOC_ZONES_PATH] "Sets BIND zones path")
            (@arg ZONES_CHROOT_PATH: -r --("zones-chroot-path") +takes_value env[NOC_ZONES_CHROOT_PATH] "Sets BIND zones path in chroot")
            (@arg HOST: -h --host env[NOC_HOST] +takes_value +required "Nameserver name")
            (@arg REQUEST_LIMIT: -l --("request-limit") "DataStream request limit")
            (@arg ERROR_TIMEOUT: -t --("error-timeout") "Timeout after error request")
            (@arg INSECURE: --("allow-insecure") "Disable SSL certificate checking")
            (@arg DAEMON: -d --daemon "Run as daemon")
            (@arg DRY_RUN: --("dry-run") "Do not apply BIND configuration")
        )
        .get_matches_from_safe(args).map(|m| {
            Self {
                api_key: m.value_of("API_KEY").unwrap().to_string(),
                noc_url: m.value_of("NOC_URL").unwrap().to_string(),
                zones_path: m.value_of("ZONES_PATH").unwrap().to_string(),
                zones_chroot_path: m.value_of("ZONES_CHROOT_PATH").map(|e| e.to_string()),
                host: m.value_of("HOST").unwrap().to_string(),
                request_limit: value_t!(m, "REQUEST_LIMIT", usize).unwrap_or(DEFAULT_REQUEST_LIMIT),
                error_timeout: value_t!(m, "ERROR_TIMEOUT", u64).unwrap_or(DEFAULT_ERR_TIMEOUT),
                insecure: m.is_present("INSECURE"),
                daemon: m.is_present("DAEMON"),
                dry_run: m.is_present("DRY_RUN"),
                verbose: m.is_present("VERBOSE"),
            }
        });
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use clap::crate_name;

    #[test]
    fn test_no_args() {
        CmdArgs::new_from([crate_name!()].iter()).unwrap_err();
    }

    #[test]
    fn test_help() {
        CmdArgs::new_from([crate_name!(), "--help"].iter()).unwrap_err();
    }
}
