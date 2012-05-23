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
//
/*
        def f():
        if last_start==last_end:
            return str(last_start)
        else:
            return "%d-%d"%(last_start,last_end)
    last_start=None
    last_end=None
    r=[]
    for i in sorted(s):
        if last_end is not None and i==last_end+1:
            last_end+=1
        else:
            if last_start is not None:
                r+=[f()]
            last_start=i
            last_end=i
    if last_start is not None:
        r+=[f()]
    return ",".join(r)
*/
NOC.listToRanges = function(lst) {
    var l = lst.sort(function(x, y){return x - y;}),
        lastStart = null,
        lastEnd = null,
        r = [],
        f = function() {
            if(lastStart == lastEnd) {
                return lastStart.toString();
            } else {
                return lastStart.toString() + "-" + lastEnd.toString();
            }
        };

    for(var i = 0; i < l.length; i++) {
        var v = l[i];
        if(lastEnd && (v == lastEnd + 1)) {
            lastEnd += 1;
        } else {
            if(lastStart != null) {
                r = r.concat(f());
            }
            lastStart = v;
            lastEnd = v;
        }
    }
    if(lastStart != null) {
        r = r.concat(f());
    }
    return r.join(",")
};
