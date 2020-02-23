/* ---------------------------------------------------------------------
 * Change template and ChangeService trait
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
use crate::error::Error;

#[derive(Debug, Deserialize)]
pub struct Change<T> {
    pub change_id: String,
    pub id: String,
    #[serde(rename(deserialize = "$deleted"))]
    #[serde(default)]
    _is_deleted: bool,
    #[serde(flatten)]
    pub data: Option<T>,
}

pub trait ChangeService<T> {
    // Process object changes
    fn change(&mut self, change: &Change<T>) -> Result<(), Error>;
    // Process object deletion
    fn delete(&mut self, change: &Change<T>) -> Result<(), Error>;
    // Apply pending changes if any
    fn apply(&mut self) -> Result<(), Error>;
}

impl<T> Change<T> {
    pub fn is_deleted(&self) -> bool {
        self._is_deleted || self.data.is_none()
    }
}

pub fn clean_change_id(s: String) -> Result<String, Error> {
    let mut ss = Clone::clone(&s);
    ss.retain(|c| !c.is_whitespace());
    Ok(ss)
}

pub type ChangeVec<T> = Vec<Change<T>>;
