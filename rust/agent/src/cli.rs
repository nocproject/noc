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
    pub config: Option<String>,
    pub bootstrap_state: Option<String>,
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
            )
            .arg(
                Arg::with_name("config")
                    .short("c")
                    .long("config")
                    .value_name("FILE")
                    .takes_value(true)
                    .help("Load config from file"),
            )
            .arg(
                Arg::with_name("bootstrap")
                    .short("s")
                    .long("bootstrap-state")
                    .value_name("FILE")
                    .takes_value(true)
                    .help("Bootstrap state file"),
            );

        let matches = app
            .get_matches_from_safe(args)
            .map_err(|e| AgentError::CliError(e.to_string()))?;
        Ok(Self {
            verbose: matches.is_present("verbose"),
            config: matches.value_of("config").map(|c| c.into()),
            bootstrap_state: matches.value_of("bootstrap").map(|c| c.into()),
        })
    }
}
