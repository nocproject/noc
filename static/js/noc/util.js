//----------------------------------------------------------------------
// Various javascript utilities
//----------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

// NOC namespace
Ext.namespace("NOC", "NOC.render");
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

NOC.render.Bool = noc_renderBool;
NOC.render.URL = noc_renderURL;
NOC.render.Tags = noc_renderTags;

NOC.render.Lookup = function(name) {
    var l = name + "__label";
    return function(value, meta, record) {
        if(value) {
            return record.get(l)
        } else {
            return "";
        }
    };
};

//
// Run new Map/Reduce task
// Usage:
// NOC.mrt({
//      url: ...,
//      selector: ...,
//      scope: ...,
//      success: ...,
//      failure: ...,
//      mapParams: ...,
// });
//
NOC.mrt = function(options) {
    var m = Ext.create("NOC.core.MRT", options);
    m.run();
}
//
NOC.error = function(msg) {
    Ext.MessageBox.show({
        title: "Error!",
        msg: Ext.String.format.apply(this, arguments),
        buttons: Ext.MessageBox.OK,
        icon: Ext.MessageBox.ERROR
    });
};
//
NOC.info = function(msg) {
    Ext.MessageBox.show({
        title: "Info",
        msg: Ext.String.format.apply(this, arguments),
        buttons: Ext.MessageBox.OK,
        icon: Ext.MessageBox.INFO
    });
};
//
NOC.hasPermission = function(perm) {
    return function(app) {
        return app.hasPermission(perm);
    }
};
