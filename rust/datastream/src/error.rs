/* ---------------------------------------------------------------------
 * Error types
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */
#[derive(Debug)]
pub enum Error {
    IOError(String),
    NotConfiguredError(String),
    SyncStateError(String),
    ParseError(String),
    ChangeError(String),
    FetchError(String),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match *self {
            Error::IOError(ref e) => e.fmt(f),
            Error::NotConfiguredError(ref e) => e.fmt(f),
            Error::SyncStateError(ref e) => e.fmt(f),
            Error::ParseError(ref e) => e.fmt(f),
            Error::ChangeError(ref e) => e.fmt(f),
            Error::FetchError(ref e) => e.fmt(f),
        }
    }
}

impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Error {
        Error::IOError(err.to_string())
    }
}

impl From<serde_json::Error> for Error {
    fn from(err: serde_json::Error) -> Error {
        Error::ParseError(err.to_string())
    }
}

impl From<Error> for std::io::Error {
    fn from(err: Error) -> std::io::Error {
        std::io::Error::new(std::io::ErrorKind::Other, err.to_string())
    }
}
