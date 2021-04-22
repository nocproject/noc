// ---------------------------------------------------------------------
// Command line parsing
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use crate::error::AgentError;
use clap::{crate_authors, crate_description, crate_version, App, Arg};
use std::convert::TryFrom;
use std::env::ArgsOs;

#[derive(Debug)]
pub struct CliArgs {
    pub verbose: bool,
}

impl TryFrom<ArgsOs> for CliArgs {
    type Error = AgentError;

    fn try_from(args: ArgsOs) -> Result<Self, Self::Error> {
        let app = App::new("noc-agent")
            .version(crate_version!())
            .author(crate_authors!())
            .about(crate_description!())
            .arg(
                Arg::with_name("verbose")
                    .short("v")
                    .long("verbose")
                    .help("Verbose output"),
            );
        let matches = app
            .get_matches_from_safe(args)
            .map_err(|e| AgentError::CliError(e.to_string()))?;
        Ok(Self {
            verbose: matches.is_present("verbose"),
        })
    }
}
