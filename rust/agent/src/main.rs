use agent::agent::Agent;
use agent::cmd::CmdArgs;
use std::process;

fn main() {
    // Parse command-line arguments
    let args = CmdArgs::new();
    // Configure logging
    env_logger::builder()
        .format_timestamp_millis()
        .filter_level(if args.verbose {
            log::LevelFilter::Debug
        } else {
            log::LevelFilter::Info
        })
        .init();
    // Configure agent
    let mut agent = Agent::new_from(args);
    // Run agent
    if let Err(e) = agent.run() {
        log::error!("Agent failed: {}", e);
        process::exit(2);
    }
}
