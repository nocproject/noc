// ---------------------------------------------------------------------
// Command line parsing
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use clap::{clap_app, crate_authors, crate_description, crate_version};
use std::env;
use std::ffi;

#[derive(Debug)]
pub struct CmdArgs {
    pub verbose: bool,
}

impl CmdArgs {
    pub fn new() -> Self {
        Self::new_from(env::args_os()).unwrap_or_else(|e| e.exit())
    }

    pub fn new_from<I, T>(args: I) -> Result<Self, clap::Error>
    where
        I: Iterator<Item = T>,
        T: Into<ffi::OsString> + Clone,
    {
        return clap_app!(("noc-agent") =>
            (version: crate_version!())
            (author: crate_authors!())
            (about: crate_description!())
            (@arg VERBOSE: -v --verbose "Verbose logging")
        )
        .get_matches_from_safe(args)
        .map(|m| Self {
            verbose: m.is_present("VERBOSE"),
        });
    }
}

impl Default for CmdArgs {
    fn default() -> Self {
        Self::new()
    }
}
