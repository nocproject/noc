/* ---------------------------------------------------------------------
 * DataStream ClientService trait
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::change::ChangeVec;
use crate::error::Error;

pub trait ClientService<T> {
    fn get_changes(&mut self, from: &Option<String>) -> Result<Option<ChangeVec<T>>, Error>;
}

#[cfg(feature = "client-http")]
pub mod http;
