// ---------------------------------------------------------------------
// HttpReader
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use super::super::Reader;
use crate::config::ConfigParser;
use crate::config::ZkConfig;
use crate::error::AgentError;
use crate::meta::VERSION;
use crate::state::AgentState;
use crate::sysid::SysId;
use async_trait::async_trait;

pub struct HttpReader {
    path: String,
    disable_cert_validation: bool,
    querystring: String,
    key_header: Option<String>,
}

pub struct HttpReaderBuilder {
    path: Option<String>,
    disable_cert_validation: bool,
    querystring: String,
    key_header: Option<String>,
}

impl HttpReader {
    pub fn builder() -> HttpReaderBuilder {
        HttpReaderBuilder {
            path: None,
            disable_cert_validation: false,
            querystring: format!("version={}", VERSION),
            key_header: None,
        }
    }
}

impl HttpReaderBuilder {
    pub fn with_path(&mut self, path: String) -> &mut Self {
        self.path = Some(path);
        self
    }
    pub fn with_cert_validation(&mut self, cert_validation: bool) -> &mut Self {
        self.disable_cert_validation = !cert_validation;
        self
    }
    pub fn with_agent_state(&mut self, state: Option<&AgentState>) -> &mut Self {
        if let Some(s) = state {
            let mut qs: Vec<String> = vec![self.querystring.clone()];
            // Agent id
            if let Some(agent_id) = s.agent_id {
                qs.push(format!("agent_id={}", agent_id));
            }
            //
            if let Some(key_header) = s.agent_key.clone() {
                self.key_header = Some(key_header)
            }
            self.querystring = qs.join("&");
        }
        self
    }
    pub fn with_sys_id(&mut self, sys_id: Option<&SysId>) -> &mut Self {
        if let Some(s) = sys_id {
            let mut qs: Vec<String> = vec![self.querystring.clone()];
            // MAC
            if !s.mac.is_empty() {
                qs.extend(s.mac.iter().map(|v| format!("mac={}", v)))
            }
            // IP
            if !s.ip.is_empty() {
                qs.extend(s.ip.iter().map(|v| format!("ip={}", v)))
            }
            //
            self.querystring = qs.join("&");
        }
        self
    }
    pub fn build(&self) -> HttpReader {
        HttpReader {
            path: self.path.as_ref().unwrap().clone(),
            disable_cert_validation: self.disable_cert_validation,
            querystring: self.querystring.clone(),
            key_header: self.key_header.clone(),
        }
    }
}

#[async_trait]
impl Reader for HttpReader {
    async fn get_config(&self) -> Result<ZkConfig, AgentError> {
        // Build full url
        let url = match &self.path.find('?') {
            Some(_) => format!("{}&{}", self.path, self.querystring),
            None => format!("{}?{}", self.path, self.querystring),
        };
        log::debug!("Reading config file: {}", url);
        // Request
        let client = reqwest::Client::builder()
            .gzip(true)
            .danger_accept_invalid_certs(self.disable_cert_validation)
            .build()
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        let mut req = client.get(url);
        if let Some(agent_key) = &self.key_header {
            req = req.header("X-NOC-Agent-Key", agent_key);
        }
        let resp = req
            .send()
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        if !resp.status().is_success() {
            return Err(AgentError::InternalError(format!(
                "Invalid response status: {}",
                resp.status().as_u16()
            )));
        }
        // Analyze content-type
        let content_type = match resp.headers().get("content-type") {
            Some(ct) => ct
                .to_str()
                .map_err(|e| AgentError::InternalError(e.to_string()))?
                .to_owned(),
            None => "text/json".to_string(),
        };
        // Pass to config parser
        let data = resp
            .bytes()
            .await
            .map_err(|e| AgentError::InternalError(e.to_string()))?;
        ConfigParser::from_content_type(data.to_vec(), &content_type)
    }
}
