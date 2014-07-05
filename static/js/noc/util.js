//----------------------------------------------------------------------
// Various javascript utilities
//----------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

// NOC namespace
Ext.namespace("NOC", "NOC.render");

//
// Custom column renderers
//
Ext.apply(NOC.render, {
    //
    // NOC.render.Bool(v)
    //     Grid field renderer for boolean values
    //     Displays icons depending on true/false status
    //
    Bool: function (v) {
        return {
            true: "<i class='fa fa-check' style='color:" + NOC.colors.yes + "'></i>",
            false: "<i class='fa fa-times' style='color:" + NOC.colors.no + "'></i>",
            null: "<i class='fa fa-circle-o'></i>"
        }[v];
    },

    //
    // NOC.render.URL(v)
    //      Grid field renderer for URLs
    //
    URL: function (v) {
        return "<a href =' " + v + "' target='_'>" + v + "</a>";
    },

    //
    // NOC.render.Tags(v)
    //      Grid field renderer for tags
    //
    Tags: function (v) {
        if (v) {
            return v.map(function (x) {
                return "<span class='x-display-tag'>" + x + "</span>";
            }).join(" ");
        } else {
            return "";
        }
    },

    Lookup: function(name) {
        var l = name + "__label";
        return function(value, meta, record) {
            if(value) {
                return record.get(l)
            } else {
                return "";
            }
        };
    },

    Clickable: function(value) {
        return "<a href='#' class='noc-clickable-cell'>" + value + "</a>";
    },

    ClickableLookup: function(name) {
        var l = name + "__label";
        return function(value, meta, record) {
            var v = value ? record.get(l) : "...";
            return "<a href='#' class='noc-clickable-cell' title='Click to change...'>" + v + "</a>";
        };
    },

    WrapColumn: function (val){
        return '<div style="white-space:normal !important;">'+ val +'</div>';
    },

    Date: function(val) {
        if(!val) {
            return "";
        }
        return Ext.Date.format(val, "Y-m-d")
    },

    DateTime: function(val) {
        if(!val) {
            return "";
        }
        return Ext.Date.format(val, "Y-m-d H:i:s")
    },

    Choices: function(choices) {
        return function(value) {
            return choices[value];
        }
    },

    Timestamp: function(val) {
        if(!val) {
            return "";
        }
        var d = new Date(val * 1000),
            y = d.getFullYear(),
            m = d.getMonth() + 1,
            D = d.getDate(),
            h = d.getHours(),
            M = d.getMinutes(),
            s = d.getSeconds(),
            f = function(v) {
                return v <= 9 ? '0' + v : v;
            };
        return "" + y + "-" + f(m) + "-" + f(D) + " " +
            f(h) + ":" + f(M) + ":" + f(s);
    },

    Duration: function(val) {
        var f = function(v) {
            return v <= 9 ? '0' + v : v;
        };

        if(!val) {
            return "";
        }
        val = +val;
        if(isNaN(val)) {
            return "";
        }
        if(val < 60) {
            // XXs
            return "" + val + "s";
        }
        if(val < 86400) {
            // HH:MM:SS
            var h = Math.floor(val / 3600),
                m = Math.floor((val - h * 3600) / 60),
                s = val - h * 3600 - m * 60;

            return f(h) + ":" + f(m) + ":" + f(s);
        }
        // DDd HHh
        var d = Math.floor(val / 86400),
            h = Math.floor((val - d * 86400) / 3600);
        return "" + d + "d " + f(h) + "h";
    },

    Size: function(v) {
        if (v === null || v === undefined) {
            return "";
        }
        if(v > 10000000) {
            return Math.round(v / 1000000) + "M";
        }
        if(v > 1000) {
            return Math.round(v / 1000) + "K";
        }
        return "" + v;
    },

    Join: function(sep) {
        return function(value) {
            return value.join(sep);
        }
    }
});

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
//
//validate function def
//
NOC.is_vlanid = function(value) {
    if (value >= 1 && value <= 4095) {
        return true;
    } else {
        return false;
    }
};
//
NOC.is_asn = function(value) {
    if (value > 0) {
        return true;
    } else {
        return false;
    }
};
//
NOC.is_ipv4 = function(value) {
    var arrayX = new Array(),
        arrayoct = new Array(),
        arrayX = value.split(".");
    if (arrayX.length != 4)
        return false;
    else {
        for (var oct in arrayX) {
            if ((parseInt(arrayX[oct]) >= 0) && (parseInt(arrayX[oct]) <=255))
                arrayoct.push(arrayX[oct]);
        }
        if (arrayoct.length != 4) {
            return false;
        } else {
            return true;
        }
    }
};
//
NOC.is_ipv4_prefix = function(value) {
    var arrayX = new Array(),
        arrayX = value.split("/");
    if (arrayX.length != 2)
        return false;
    if (!NOC.is_ipv4(arrayX[0]))
        return false;
    if ((parseInt(arrayX[1]) >= 0) && (parseInt(arrayX[1]) <= 32)) {
        return true;
    } else {
        return false;
    }
};
//
// init quick labels for vtype validators
Ext.QuickTips.init();
Ext.form.Field.prototype.msgTarget = 'side';

//
// Custom VTypes
//
Ext.apply(Ext.form.field.VTypes, {
    // VLAN ID checking
    VlanID: function(val, field) {
        try {
            var id = parseInt(val);
            return NOC.is_vlanid(id);
        } catch(e) {
            return false;
        }
    },
    VlanIDText: "Must be a numeric value [1-4095]",
    VlanIDMask: /[\d\/]/,

    // Autonomous system name checking
    ASN: function(val, field) {
        try {
            var asn = parseInt(val);
            return NOC.is_asn(asn);
        } catch(e) {
            return false;
        }
    },
    ASNText: "AS num must be a numeric value > 0",
    ASNMask: /[\d\/]/,

    // IPv4 check
    IPv4: function(val, field){
        try {
            return NOC.is_ipv4(val);
        } catch(e) {
            return false;
        }
    },
    IPv4Text: "Must be a numeric value 0.0.0.0 - 255.255.255.255",
    IPv4Mask: /[\d\.]/i,

    // IPv4 prefix check
    IPv4Prefix: function(val, field){
        try {
            return NOC.is_ipv4_prefix(val);
        } catch(e) {
            return false;
        }
    },
    IPv4PrefixText: "Must be a numeric value 0.0.0.0/0 - 255.255.255.255/32",
    IPv4PrefixMask: /[\d\.\/]/i,

    // FQDN check
    FQDN: function(val, field){
        var me = this;
        try {
            return me.FQDNMask.test(val);
        } catch(e) {
            return false;
        }
    },
    FQDNText: "Not valid FQDN",
    FQDNMask: /^([a-z0-9\-]+\.)+[a-z0-9\-]+$/i,

    // AS-set check
    ASSET: function(val, field){
        var me = this;
        try {
            return me.ASSETMask.test(val);
        } catch(e) {
            return false;
        }
    },   
    ASSETText: "Not valid ASSET, must be in form AS-SET or AS-MEGA-SET",
    ASSETMask: /^AS(-\w+)+$/i,

    // AS/AS-set check
    ASorASSET: function(val, field){
        var me = this;
        return me.ASN(val, field) || me.ASSET(val, field);
    },
    ASorASSETText: "Not valid AS or ASSET, must be in form AS3505, AS-SET, AS-MEGA-SET or AS3245:AS-TEST",

    // Color check
    color: function(val, field) {
        var me = this;
        return me.colorMask.test(val);
    },
    colorMask: /^[0-9a-f]{6}$/i,
    colorText: "Invalid color, must be 6 hexadecimals"
});

//
// Handlebars helpers
//
Handlebars.registerHelper("debug", function(opt) {
  console.log("Current context: ", this);

  if (arguments.length > 1) {
    console.log("Value:", opt);
  }
});

Handlebars.registerHelper("join", function(context, block) {
    return context.map(function(v) {
        return block.fn(v);
    }).join(", ");
});

Handlebars.registerHelper("formatDuration", NOC.render.Duration);

Handlebars.registerHelper("grid", function(val) {
    var r = [],
        xset = {},
        yset = {},
        values = {},
        i, j, y, v,
        xv = [],
        yv = [];
    // Get all unique x and y
    for(i in val) {
        v = val[i];
        if(!xset[v.x]) {
            xset[v.x] = true;
            xv.push(v.x);
        }
        if(!yset[v.y]) {
            yset[v.y] = true;
            yv.push(v.y);
        }
        if(!values[v.x]) {
            values[v.x] = {};
        }
        values[v.x][v.y] = v.v;
    }
    xv = xv.sort();
    yv = yv.sort();
    //
    // Build table
    //
    r.push("<table border='1'>");
    // Push header
    r.push("<tr><td></td>");
    for(i in xv) {
        r.push("<th>");
        r.push(Handlebars.Utils.escapeExpression(xv[i]));
        r.push("</th>");
    }
    r.push("</tr>");
    // Push rows
    for(i in yv) {
        y = yv[i];
        r.push("<tr>");
        r.push("<th>");
        r.push(Handlebars.Utils.escapeExpression(y));
        r.push("</th>");
        for(j in xv) {
            v = xv[j];
            r.push("<td>");
            if(values[v] && values[v][y] !== undefined) {
                r.push(Handlebars.Utils.escapeExpression(values[v][y]));
            }
            r.push("</td>");
        }
        r.push("</tr>");
    }
    r.push("</table>");
    // return r.join("");
    return new Handlebars.SafeString(r.join(""));
});
