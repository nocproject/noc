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

//
// Run new Map/Reduce task
// Usage:
// NOC.mrt({
//      url: ...,
//      selector: ...,
//      scope: ...,
//      success: ...,
//      failure: ...,
// });
//
NOC.mrt = function(config) {
    var scope = config.scope || this,
        checkMRT = function(task) {
            Ext.Ajax.request({
                url: config.url + task + "/",
                method: "GET",
                success: function(response) {
                    var r = Ext.decode(response.responseText);
                    if(r.ready) {
                        // MRT finished
                        if(config.success)
                            config.success.call(scope, r.result);
                    } else {
                        // Wait and recheck
                        Ext.defer(Ext.bind(checkMRT, this, [task]), 1000);
                    }
                },
                failure: function() {
                    if (config.failure)
                        config.failure.call(scope);
                }
            });
        };

    Ext.Ajax.request({
        url: config.url,
        method: "POST",
        jsonData: {
            selector: config.selector
        },
        success: function(response) {
            checkMRT(Ext.decode(response.responseText));
        },
        failure: function() {
            if(config.failure)
                config.failure.call(scope);
        }
    });
};
//
NOC.error = function(msg) {
    Ext.MessageBox.show({
        title: "Error!",
        msg: Ext.String.format.apply(this, arguments),
        buttons: Ext.MessageBox.OK,
        icon: Ext.MessageBox.ERROR
    });
};
