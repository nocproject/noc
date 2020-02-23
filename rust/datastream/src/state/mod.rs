/* ---------------------------------------------------------------------
 * <describe module here>
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::error::Error;

pub trait StateService {
    // Get last processed Change ID
    fn get_last_change_id(&mut self) -> Result<Option<String>, Error>;
    // Register successfully processed object
    fn register_change_id(&mut self, change_id: &String) -> Result<(), Error>;
    // Finally apply pending changes if any
    fn apply(&mut self) -> Result<(), Error>;
}

#[cfg(feature = "state-memory")]
pub mod memory;

#[cfg(feature = "state-plain")]
pub mod plain;
