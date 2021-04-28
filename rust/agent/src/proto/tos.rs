// ---------------------------------------------------------------------
// ToS/DSCP manipulation
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    static ref DSCP_TO_TOS_MAP: HashMap<&'static str, u8> = {
        let mut m = HashMap::new();
        m.insert("be", 0);
        m.insert("cp1", 1);
        m.insert("cp2", 2);
        m.insert("cp3", 3);
        m.insert("cp4", 4);
        m.insert("cp5", 5);
        m.insert("cp6", 6);
        m.insert("cp7", 7);
        m.insert("cs1", 8);
        m.insert("cp9", 9);
        m.insert("af11", 10);
        m.insert("cp11", 11);
        m.insert("af12", 12);
        m.insert("cp13", 13);
        m.insert("af13", 14);
        m.insert("cp15", 15);
        m.insert("cs2", 16);
        m.insert("cp17", 17);
        m.insert("af21", 18);
        m.insert("cp19", 19);
        m.insert("af22", 20);
        m.insert("cp21", 21);
        m.insert("af23", 22);
        m.insert("cp23", 23);
        m.insert("cs3", 24);
        m.insert("cp25", 25);
        m.insert("af31", 26);
        m.insert("cp27", 27);
        m.insert("af32", 28);
        m.insert("cp29", 29);
        m.insert("af33", 30);
        m.insert("cp31", 31);
        m.insert("cs4", 32);
        m.insert("cp33", 33);
        m.insert("af41", 34);
        m.insert("cp35", 35);
        m.insert("af42", 36);
        m.insert("cp37", 37);
        m.insert("af43", 38);
        m.insert("cp39", 39);
        m.insert("cs5", 40);
        m.insert("cp41", 41);
        m.insert("cp42", 42);
        m.insert("cp43", 43);
        m.insert("cp44", 44);
        m.insert("cp45", 45);
        m.insert("ef", 46);
        m.insert("cp47", 47);
        m.insert("nc1", 48);
        m.insert("cp49", 49);
        m.insert("cp50", 50);
        m.insert("cp51", 51);
        m.insert("cp52", 52);
        m.insert("cp53", 53);
        m.insert("cp54", 54);
        m.insert("cp55", 55);
        m.insert("nc2", 56);
        m.insert("cp57", 57);
        m.insert("cp58", 58);
        m.insert("cp59", 59);
        m.insert("cp60", 60);
        m.insert("cp61", 61);
        m.insert("cp62", 62);
        m.insert("cp63", 63);
        m
    };
    static ref TOS_TO_DSCP_MAP: HashMap<u8, &'static str> = {
        let mut m = HashMap::new();
        m.insert(0, "be");
        m.insert(1, "cp1");
        m.insert(2, "cp2");
        m.insert(3, "cp3");
        m.insert(4, "cp4");
        m.insert(5, "cp5");
        m.insert(6, "cp6");
        m.insert(7, "cp7");
        m.insert(8, "cs1");
        m.insert(9, "cp9");
        m.insert(10, "af11");
        m.insert(11, "cp11");
        m.insert(12, "af12");
        m.insert(13, "cp13");
        m.insert(14, "af13");
        m.insert(15, "cp15");
        m.insert(16, "cs2");
        m.insert(17, "cp17");
        m.insert(18, "af21");
        m.insert(19, "cp19");
        m.insert(20, "af22");
        m.insert(21, "cp21");
        m.insert(22, "af23");
        m.insert(23, "cp23");
        m.insert(24, "cs3");
        m.insert(25, "cp25");
        m.insert(26, "af31");
        m.insert(27, "cp27");
        m.insert(28, "af32");
        m.insert(29, "cp29");
        m.insert(30, "af33");
        m.insert(31, "cp31");
        m.insert(32, "cs4");
        m.insert(33, "cp33");
        m.insert(34, "af41");
        m.insert(35, "cp35");
        m.insert(36, "af42");
        m.insert(37, "cp37");
        m.insert(38, "af43");
        m.insert(39, "cp39");
        m.insert(40, "cs5");
        m.insert(41, "cp41");
        m.insert(42, "cp42");
        m.insert(43, "cp43");
        m.insert(44, "cp44");
        m.insert(45, "cp45");
        m.insert(46, "ef");
        m.insert(47, "cp47");
        m.insert(48, "nc1");
        m.insert(49, "cp49");
        m.insert(50, "cp50");
        m.insert(51, "cp51");
        m.insert(52, "cp52");
        m.insert(53, "cp53");
        m.insert(54, "cp54");
        m.insert(55, "cp55");
        m.insert(56, "nc2");
        m.insert(57, "cp57");
        m.insert(58, "cp58");
        m.insert(59, "cp59");
        m.insert(60, "cp60");
        m.insert(61, "cp61");
        m.insert(62, "cp62");
        m.insert(63, "cp63");
        m
    };
}

pub fn dscp_to_tos(dscp: String) -> Option<u8> {
    match DSCP_TO_TOS_MAP.get(dscp.as_str()) {
        Some(x) => Some(*x),
        None => None,
    }
}

pub fn tos_to_dscp(tos: u8) -> Option<&'static str> {
    match TOS_TO_DSCP_MAP.get(&tos) {
        Some(x) => Some(*x),
        None => None,
    }
}

#[cfg(test)]
mod tests {
    use crate::proto::tos::dscp_to_tos;

    #[test]
    fn test_dscp_to_tos() {
        assert_eq!(dscp_to_tos("be".into()), Some(0));
        assert_eq!(dscp_to_tos("cp1".into()), Some(1));
        assert_eq!(dscp_to_tos("cp2".into()), Some(2));
        assert_eq!(dscp_to_tos("cp3".into()), Some(3));
        assert_eq!(dscp_to_tos("cp4".into()), Some(4));
        assert_eq!(dscp_to_tos("cp5".into()), Some(5));
        assert_eq!(dscp_to_tos("cp6".into()), Some(6));
        assert_eq!(dscp_to_tos("cp7".into()), Some(7));
        assert_eq!(dscp_to_tos("cs1".into()), Some(8));
        assert_eq!(dscp_to_tos("cp9".into()), Some(9));
        assert_eq!(dscp_to_tos("af11".into()), Some(10));
        assert_eq!(dscp_to_tos("cp11".into()), Some(11));
        assert_eq!(dscp_to_tos("af12".into()), Some(12));
        assert_eq!(dscp_to_tos("cp13".into()), Some(13));
        assert_eq!(dscp_to_tos("af13".into()), Some(14));
        assert_eq!(dscp_to_tos("cp15".into()), Some(15));
        assert_eq!(dscp_to_tos("cs2".into()), Some(16));
        assert_eq!(dscp_to_tos("cp17".into()), Some(17));
        assert_eq!(dscp_to_tos("af21".into()), Some(18));
        assert_eq!(dscp_to_tos("cp19".into()), Some(19));
        assert_eq!(dscp_to_tos("af22".into()), Some(20));
        assert_eq!(dscp_to_tos("cp21".into()), Some(21));
        assert_eq!(dscp_to_tos("af23".into()), Some(22));
        assert_eq!(dscp_to_tos("cp23".into()), Some(23));
        assert_eq!(dscp_to_tos("cs3".into()), Some(24));
        assert_eq!(dscp_to_tos("cp25".into()), Some(25));
        assert_eq!(dscp_to_tos("af31".into()), Some(26));
        assert_eq!(dscp_to_tos("cp27".into()), Some(27));
        assert_eq!(dscp_to_tos("af32".into()), Some(28));
        assert_eq!(dscp_to_tos("cp29".into()), Some(29));
        assert_eq!(dscp_to_tos("af33".into()), Some(30));
        assert_eq!(dscp_to_tos("cp31".into()), Some(31));
        assert_eq!(dscp_to_tos("cs4".into()), Some(32));
        assert_eq!(dscp_to_tos("cp33".into()), Some(33));
        assert_eq!(dscp_to_tos("af41".into()), Some(34));
        assert_eq!(dscp_to_tos("cp35".into()), Some(35));
        assert_eq!(dscp_to_tos("af42".into()), Some(36));
        assert_eq!(dscp_to_tos("cp37".into()), Some(37));
        assert_eq!(dscp_to_tos("af43".into()), Some(38));
        assert_eq!(dscp_to_tos("cp39".into()), Some(39));
        assert_eq!(dscp_to_tos("cs5".into()), Some(40));
        assert_eq!(dscp_to_tos("cp41".into()), Some(41));
        assert_eq!(dscp_to_tos("cp42".into()), Some(42));
        assert_eq!(dscp_to_tos("cp43".into()), Some(43));
        assert_eq!(dscp_to_tos("cp44".into()), Some(44));
        assert_eq!(dscp_to_tos("cp45".into()), Some(45));
        assert_eq!(dscp_to_tos("ef".into()), Some(46));
        assert_eq!(dscp_to_tos("cp47".into()), Some(47));
        assert_eq!(dscp_to_tos("nc1".into()), Some(48));
        assert_eq!(dscp_to_tos("cp49".into()), Some(49));
        assert_eq!(dscp_to_tos("cp50".into()), Some(50));
        assert_eq!(dscp_to_tos("cp51".into()), Some(51));
        assert_eq!(dscp_to_tos("cp52".into()), Some(52));
        assert_eq!(dscp_to_tos("cp53".into()), Some(53));
        assert_eq!(dscp_to_tos("cp54".into()), Some(54));
        assert_eq!(dscp_to_tos("cp55".into()), Some(55));
        assert_eq!(dscp_to_tos("nc2".into()), Some(56));
        assert_eq!(dscp_to_tos("cp57".into()), Some(57));
        assert_eq!(dscp_to_tos("cp58".into()), Some(58));
        assert_eq!(dscp_to_tos("cp59".into()), Some(59));
        assert_eq!(dscp_to_tos("cp60".into()), Some(60));
        assert_eq!(dscp_to_tos("cp61".into()), Some(61));
        assert_eq!(dscp_to_tos("cp62".into()), Some(62));
        assert_eq!(dscp_to_tos("cp63".into()), Some(63));
        assert_eq!(dscp_to_tos("foobar".into()), None);
    }
}
