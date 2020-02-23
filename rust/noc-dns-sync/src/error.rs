/* ---------------------------------------------------------------------
 * Error types
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */

#[derive(Debug)]
pub enum Error {
    IOError(std::io::Error),
    PunicodeError,
    ParseError(String),
    NotConfiguredError(String),
    DataStreamError(String),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match *self {
            Error::IOError(ref e) => e.fmt(f),
            Error::PunicodeError => write!(f, "Punicode decode error"),
            Error::ParseError(ref s) => write!(f, "Failed to parse: {}", s),
            Error::NotConfiguredError(ref e) => e.fmt(f),
            Error::DataStreamError(ref e) => e.fmt(f),
        }
    }
}

impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Error {
        Error::IOError(err)
    }
}

impl From<std::num::ParseIntError> for Error {
    fn from(err: std::num::ParseIntError) -> Error {
        Error::ParseError(err.to_string())
    }
}

impl From<Error> for std::io::Error {
    fn from(err: Error) -> std::io::Error {
        std::io::Error::new(std::io::ErrorKind::Other, err.to_string())
    }
}

impl From<datastream::error::Error> for Error {
    fn from(err: datastream::error::Error) -> Error {
        Error::DataStreamError(err.to_string())
    }
}
