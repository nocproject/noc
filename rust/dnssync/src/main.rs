/* ---------------------------------------------------------------------
 * DataStream DNS Synchronization service
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use datastream::client::http::HttpClientService;
use datastream::state::plain::PlainStateService;
use datastream::sync::SyncService;
use log::warn;
use std::path::Path;

mod error;

mod cmd;
use crate::cmd::CmdArgs;

mod dnszone;
use crate::dnszone::DNSZone;

mod change;
use crate::change::bind::BindChangeService;

const CHANGEID_PATH: &str = ".changeid";

// Build and run BIND synchronizer
#[cfg(feature = "bind")]
fn run_bind_sync_service(args: &CmdArgs) -> Result<(), std::io::Error> {
    warn!("Starting BIND sync service");
    let state_path = Path::new(&args.zones_path)
        .join(CHANGEID_PATH)
        .into_os_string()
        .into_string()
        .unwrap();
    let mut state_service = PlainStateService::new().path(&state_path).build()?;
    let mut client_service = HttpClientService::<DNSZone>::new()
        .url(&args.noc_url)
        .api_key(&args.api_key)
        .insecure(args.insecure)
        .stream(&String::from("dnszone"))
        .filter(&format!("server({})", &args.host))
        .build()?;
    let mut change_service = BindChangeService::new()
        .zones_path(&args.zones_path)
        .zones_chroot_path(&args.zones_chroot_path.as_ref().unwrap_or(&String::from("")))
        .dry_run(args.dry_run)
        .build()?;
    let mut sync_service =
        SyncService::new_from(&mut client_service, &mut change_service, &mut state_service)?;
    sync_service.run()?;
    warn!("Stopping");
    Ok(())
}

fn main() -> Result<(), std::io::Error> {
    let args = CmdArgs::new();
    env_logger::builder()
        .format_timestamp_secs()
        .filter_level(if args.verbose {
            log::LevelFilter::Debug
        } else {
            log::LevelFilter::Info
        })
        .init();
    run_bind_sync_service(&args)?;
    Ok(())
}
