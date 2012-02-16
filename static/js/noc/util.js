//----------------------------------------------------------------------
// Various javascript utilities
//----------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

//
// Setup
//
_noc_bool_img = {
    true: "<img src='/static/img/fam/silk/accept.png' />",
    false: "<img src='/static/img/fam/silk/cancel.png' />",
    null: "<img src='/static/img/fam/silk/bullet_black.png' />"
};

//
// renderBool(v)
//     Grid field renderer for boolean values
//     Displays icons depending on true/false status
//
function noc_renderBool(v) {
    return _noc_bool_img[v];
}