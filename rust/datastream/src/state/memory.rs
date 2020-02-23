/* ---------------------------------------------------------------------
 * In-memory State Service
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::error::Error;
use crate::state::StateService;
use log::{debug, info};

pub struct MemoryStateService {
    last_change_id: Option<String>,
}

impl MemoryStateService {
    pub fn new() -> MemoryStateServiceBuilder {
        info!("Initializing memory state service");
        MemoryStateServiceBuilder
    }
}

pub struct MemoryStateServiceBuilder;

impl MemoryStateServiceBuilder {
    pub fn build(&mut self) -> Result<MemoryStateService, Error> {
        info!("Memory state service is running");
        Ok(MemoryStateService {
            last_change_id: None,
        })
    }
}

impl StateService for MemoryStateService {
    // Get last processed Change ID
    fn get_last_change_id(&mut self) -> Result<Option<String>, Error> {
        Ok(self.last_change_id.clone())
    }
    // Register successfully processed object
    fn register_change_id(&mut self, change_id: &String) -> Result<(), Error> {
        debug!("Register change id: {}", &change_id);
        self.last_change_id = Some(change_id.clone());
        Ok(())
    }
    // Finally apply pending changes if any
    fn apply(&mut self) -> Result<(), Error> {
        Ok(())
    }
}
