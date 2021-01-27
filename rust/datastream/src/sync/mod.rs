/* ---------------------------------------------------------------------
 * DataStream SyncService
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2021 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::change::ChangeService;
use crate::client::ClientService;
use crate::error::Error;
use crate::state::StateService;
use log::{error, info};
use std::marker::PhantomData;

const DEFAULT_ERR_TIMEOUT: u64 = 5;
const MIN_PULL_TIME: u64 = 1000; // ms

pub struct SyncService<'a, T, Cl, Ch, S>
where
    Cl: ClientService<T>,
    Ch: ChangeService<T>,
    S: StateService,
{
    client: &'a mut Cl,
    change: &'a mut Ch,
    state: &'a mut S,
    last_change_id: Option<String>,
    to_shutdown: bool,
    err_timeout: u64,
    phantom: PhantomData<T>,
}

impl<'a, T, Cl, Ch, S> SyncService<'a, T, Cl, Ch, S>
where
    Cl: ClientService<T>,
    Ch: ChangeService<T>,
    S: StateService,
{
    pub fn new_from(
        client: &'a mut Cl,
        change: &'a mut Ch,
        state: &'a mut S,
    ) -> Result<SyncService<'a, T, Cl, Ch, S>, Error> {
        Ok(SyncService {
            client: client,
            change: change,
            state: state,
            last_change_id: None,
            to_shutdown: false,
            err_timeout: DEFAULT_ERR_TIMEOUT,
            phantom: PhantomData,
        })
    }

    // Pull batch and apply changes
    fn pull_and_apply(&mut self) -> Result<(), Error> {
        // Get next chunk
        let changes = self.client.get_changes(&self.last_change_id)?;
        // Process changes, if any
        if let Some(chg) = changes {
            for c in chg.iter() {
                if c.is_deleted() {
                    self.change.delete(c)?;
                } else {
                    self.change.change(c)?;
                }
                // Save state
                self.state.register_change_id(&c.change_id)?;
            }
            // Apply changes, if any
            if let Some(c) = chg.last() {
                self.change.apply()?;
                self.state.apply()?;
                self.last_change_id = Some(c.change_id.clone())
            }
        }
        Ok(())
    }

    pub fn run(&mut self) -> Result<(), Error> {
        info!("Starting synchronization");
        // Restore state
        self.last_change_id = self.state.get_last_change_id()?;
        // Main loop
        while !self.to_shutdown {
            let now = std::time::SystemTime::now();
            if let Err(e) = self.pull_and_apply() {
                info!("Failed to pull and apply changes: {}", e);
                if !self.to_shutdown {
                    std::thread::sleep(std::time::Duration::from_secs(self.err_timeout));
                }
            }
            // DDoS prevention
            if !self.to_shutdown {
                match now.elapsed() {
                    Ok(t) => {
                        let d = t.as_millis() as u64;
                        if d < MIN_PULL_TIME {
                            // Throttle a while to suppress possible raising DDoS
                            std::thread::sleep(std::time::Duration::from_millis(MIN_PULL_TIME - d));
                        }
                    }
                    Err(_) => error!("Failed to detect elapsed time"),
                }
            }
        }
        //
        Ok(())
    }

    pub fn shutdown(&mut self) {
        self.to_shutdown = true
    }

    pub fn error_timeout(&mut self, t: u64) -> &mut Self {
        self.err_timeout = t;
        self
    }
}
