use agent::agent::Agent;
use agent::cli::CliArgs;
use agent::error::AgentError;
use std::convert::TryFrom;
use std::env;
use std::process;

fn run() -> Result<(), AgentError> {
    // Parse command-line arguments
    let args = CliArgs::try_from(env::args_os())?;
    let mut agent = Agent::try_from(args)?;
    agent.run()
}

fn main() {
    if let Err(e) = run() {
        log::error!("Agent failed: {:?}", e);
        process::exit(2);
    }
}
