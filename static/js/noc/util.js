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
    true: "<img src='/static/img/fam/silk/tick.png' />",
    false: "<img src='/static/img/fam/silk/cross.png' />",
    null: "<img src='/static/img/fam/silk/bullet_black.png' />"
};

//
// noc_renderBool(v)
//     Grid field renderer for boolean values
//     Displays icons depending on true/false status
//
function noc_renderBool(v) {
    return _noc_bool_img[v];
}

//
// noc_renderURL(v)
//      Grid field renderer for URLs
//
function noc_renderURL(v) {
    return "<a href =' " + v + "' target='_'>" + v + "</a>";
}

//
// noc_renderTags(v)
//      Grid field renderer for tags
//
function noc_renderTags(v) {
    if(v) {
        return v.map(function(x) {
            return "<span class='x-boxselect-item'>" + x + "</span>";
        }).join(" ");
    } else {
        return "";
    }
}