/* ---------------------------------------------------------------------
 * DataStream HttpClientService
 * ---------------------------------------------------------------------
 * Copyright (C) 2007-2020 The NOC Project
 * See LICENSE for details
 * ---------------------------------------------------------------------
 */

use crate::change::ChangeVec;
use crate::client::ClientService;
use crate::error::Error;
use log::{debug, error, info, max_level, LevelFilter};
use std::marker::PhantomData;

//
const DEFAULT_USER_AGENT: &str = "NOC DataStream Client";
// Default datastream limit
const DEFAULT_LIMIT: usize = 1_000;
// Default connection timeout, in millis
const DEFAULT_CONNECT_TIMEOUT: u64 = 10_000;
// Default request read timeout, in millis
const DEFAULT_READ_TIMEOUT: u64 = 60_000;

pub struct HttpClientService<T> {
    url: String,
    api_key: String,
    limit: usize,
    stream: String,
    filter: Option<String>,
    block: bool,
    phantom: PhantomData<T>,
}

impl<T> HttpClientService<T> {
    pub fn new() -> HttpClientServiceBuilder<T> {
        info!("Initializing HTTP client service");
        HttpClientServiceBuilder {
            url: None,
            api_key: None,
            limit: None,
            filter: None,
            stream: None,
            phantom: PhantomData,
        }
    }
}

pub struct HttpClientServiceBuilder<T> {
    url: Option<String>,
    stream: Option<String>,
    api_key: Option<String>,
    limit: Option<usize>,
    filter: Option<String>,
    phantom: PhantomData<T>,
}

impl<T> HttpClientServiceBuilder<T> {
    pub fn url(&mut self, url: &String) -> &mut Self {
        if url.ends_with("/") {
            self.url = Some(url.clone());
        } else {
            self.url = Some(format!("{}/", url))
        }
        self
    }

    pub fn api_key(&mut self, api_key: &String) -> &mut Self {
        self.api_key = Some(api_key.clone());
        self
    }

    pub fn limit(&mut self, limit: usize) -> &mut Self {
        self.limit = Some(limit);
        self
    }

    pub fn stream(&mut self, stream: &String) -> &mut Self {
        self.stream = Some(stream.clone());
        self
    }

    pub fn filter(&mut self, filter: &String) -> &mut Self {
        self.filter = Some(filter.clone());
        self
    }

    pub fn build(&self) -> Result<HttpClientService<T>, Error> {
        info!("HTTP client service is started");
        Ok(HttpClientService {
            url: self
                .url
                .clone()
                .ok_or(Error::NotConfiguredError(String::from("url")))?,
            api_key: self
                .api_key
                .clone()
                .ok_or(Error::NotConfiguredError(String::from("api_key")))?,
            stream: self
                .stream
                .clone()
                .ok_or(Error::NotConfiguredError(String::from("stream")))?,
            limit: self.limit.unwrap_or(DEFAULT_LIMIT),
            filter: self.filter.clone(),
            block: true,
            phantom: PhantomData,
        })
    }
}

impl<T> ClientService<T> for HttpClientService<T>
where
    T: serde::de::DeserializeOwned,
{
    fn get_changes(&mut self, from: &Option<String>) -> Result<Option<ChangeVec<T>>, Error> {
        let mut url = format!(
            "{url}api/datastream/{stream}?limit={limit}",
            url = self.url,
            stream = self.stream,
            limit = self.limit
        );
        if self.filter.is_some() {
            url = format!(
                "{url}&filter={filter}",
                url = url,
                filter = self.filter.as_ref().unwrap()
            );
        }
        if from.is_some() {
            url = format!(
                "{url}&from={from}",
                url = url,
                from = from.as_ref().unwrap()
            );
        }
        if self.block {
            url = format!("{url}&block=1", url = url);
        }
        debug!("GET {}", &url);
        // @todo: Should we use Agent?
        let resp = ureq::get(&url)
            .set("Private-Token", &self.api_key)
            .set("User-Agent", DEFAULT_USER_AGENT)
            .timeout_connect(DEFAULT_CONNECT_TIMEOUT)
            .timeout_read(DEFAULT_READ_TIMEOUT)
            .call();
        match resp.status() {
            // OK
            200 => {
                debug!("Got response");
                serde_json::from_reader(resp.into_reader())
                    .map(|v: ChangeVec<T>| if v.is_empty() { None } else { Some(v) })
                    .map_err(|e| Error::ParseError(e.to_string()))
            }
            // Gateway timeout
            504 => {
                debug!("Gateway timeout");
                Ok(None)
            }
            //
            code => {
                error!(
                    "Invalid HTTP response code: {} ({})",
                    code,
                    resp.status_text()
                );
                if max_level() >= LevelFilter::Debug {
                    // Dump response
                    debug!("Raw response:\n {}", resp.into_string()?);
                }
                Err(Error::FetchError(String::from("Invalid response code")))
            }
        }
    }
}
