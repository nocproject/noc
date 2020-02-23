/* ---------------------------------------------------------------------
 * Plain file state service
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::change::clean_change_id;
use crate::error::Error;
use crate::state::StateService;
use log::{debug, error, info};
use std::fs;
use std::path::Path;

pub struct PlainStateService {
    // File path
    path: String,
    // Last known change
    last_change_id: Option<String>,
}

impl PlainStateService {
    pub fn new() -> PlainStateServiceBuilder {
        info!("Initializing plain state service");
        PlainStateServiceBuilder { path: None }
    }
}

pub struct PlainStateServiceBuilder {
    path: Option<String>,
}

impl PlainStateServiceBuilder {
    pub fn path(&mut self, path: &String) -> &mut Self {
        self.path = Some(path.clone());
        self
    }

    pub fn build(&mut self) -> Result<PlainStateService, Error> {
        let svc = PlainStateService {
            path: self
                .path
                .clone()
                .ok_or(Error::NotConfiguredError(String::from("path")))?,
            last_change_id: None,
        };
        info!("Plain state service is initialized");
        Ok(svc)
    }
}

impl StateService for PlainStateService {
    // Get last processed Change ID
    fn get_last_change_id(&mut self) -> Result<Option<String>, Error> {
        if self.last_change_id.is_none() && Path::new(&self.path).exists() {
            // Read change id
            let buffer = fs::read_to_string(&self.path)?;
            self.last_change_id = Some(clean_change_id(buffer)?);
        }
        Ok(self.last_change_id.clone())
    }
    // Register successfully processed object
    fn register_change_id(&mut self, change_id: &String) -> Result<(), Error> {
        debug!("Register change id: {}", &change_id);
        fs::write(&self.path, change_id).map_err(|e| {
            error!("Cannot write state to {}: {}", &self.path, e);
            e
        })?;
        self.last_change_id = Some(change_id.clone());
        Ok(())
    }
    // Finally apply pending changes if any
    fn apply(&mut self) -> Result<(), Error> {
        Ok(())
    }
}
