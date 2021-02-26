// ---------------------------------------------------------------------
// Timing structure
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

/// Structure to calculate delay and jitter estimation for series of the tests.
///
/// Jitter is calculated via first-order estimator of variance D
/// with gain parameter `g` (1/16) as:
/// J[i] = (1 - g) * J[i - 1] + g * |D[i]|,
/// Where D[i] = |Delay[i] - Delay[i - 1]|
#[derive(Debug)]
pub struct Timing {
    pub min_ns: u64,
    pub max_ns: u64,
    pub avg_ns: u64,
    pub jitter_ns: u64,
    count: u64,
    last_ns: u64,
    sum_ns: u64,
}

impl Timing {
    pub fn new() -> Self {
        Self {
            min_ns: 0,
            max_ns: 0,
            avg_ns: 0,
            jitter_ns: 0,
            count: 0,
            last_ns: 0,
            sum_ns: 0,
        }
    }
    /// Register duration
    pub fn register(&mut self, delta_ns: u64) {
        let diff_ns = if delta_ns > self.last_ns {
            delta_ns - self.last_ns
        } else {
            self.last_ns - delta_ns
        };
        // J = J + (|D| - J) / 16 ==>
        // J = J - J / 16 - |D| / 16
        self.jitter_ns = self.jitter_ns - (self.jitter_ns >> 4) + (diff_ns >> 4);
        if self.count == 0 {
            self.min_ns = delta_ns;
            self.max_ns = delta_ns;
        } else {
            if self.min_ns > delta_ns {
                self.min_ns = delta_ns
            }
            if self.max_ns < delta_ns {
                self.max_ns = delta_ns
            }
        }
        self.count += 1;
        self.last_ns = delta_ns;
        self.sum_ns += delta_ns;
    }
    /// Finish measurements
    pub fn done(&mut self) {
        if self.count > 0 {
            self.avg_ns = self.sum_ns / self.count;
        }
    }
}

impl Default for Timing {
    fn default() -> Self {
        Self::new()
    }
}
