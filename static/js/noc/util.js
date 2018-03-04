//----------------------------------------------------------------------
// Various javascript utilities
//----------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

// NOC namespace
Ext.namespace("NOC", "NOC.render", "NOC.msg");

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

    Tooltip: function(fmt) {
        var tpl = new Ext.XTemplate(fmt);
        return function(value, meta, record) {
            var tooltip = tpl.apply(record.getData());
            return Ext.String.format(
                '<span title="{0}">{1}</span>',
                Ext.htmlEncode(tooltip),
                Ext.htmlEncode(value)
            );
        }
    },

    LookupTooltip: function(name, fmt) {
        var lookup = NOC.render.Lookup(name),
            tooltip = NOC.render.Tooltip(fmt);
        return function(value, meta, record) {
            return tooltip(
                lookup(value, meta, record),
                meta, record
            )
        }
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

    ArrayChoices: function(choices) {
        return function(value) {
            for(var i = 0; i < choices.length; i++) {
                var v = choices[i];
                if(value == v[0]) {
                    return v[1];
                }
            }
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
        if (val < 1) {
            // Msec
            return "" + val*1000 + "ms";
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
        if(v >= 10000000) {
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
    },

    htmlEncode: function(v) {
        if(v) return Ext.util.Format.htmlEncode(v);
        return "NULL";
    },

    //
    // NOC.render.Table accepts table configuration
    // and values as list of objects
    //
    // renderer: NOC.render.Table({
    //     columns: [
    //         {
    //             text: "Column Header 1",
    //             dataIndex: "field1"
    //         },
    //         {
    //             text: "Column Header 2",
    //             dataIndex: "field2",
    //             renderer: NOC.render.Bool
    //         }
    //     ]
    // })
    //
    Table: function(config) {
        var fields = [],
            renderers = [],
            columns = config.columns || [],
            header = ["<div class='noc-tp'>", "<table>", "<tr>"];
        Ext.each(columns, function(c) {
            fields.push(c.dataIndex || null);
            renderers.push(c.renderer || NOC.render.htmlEncode);
            header.push("<th>");
            header.push(Ext.util.Format.htmlEncode(c.text || ""));
            header.push("</th>");
        });
        header.push("</tr>");
        header = header.join("");
        return function(value) {
            var r = [header];
            if(value) {
                for(var i = 0; i < value.length; i++) {
                    var row = value[i];
                    r.push("<tr>");
                    for(var j = 0; j < fields.length; j++) {
                        r.push("<td>");
                        r.push(renderers[j](row[fields[j]]));
                        r.push("</td>");
                    }
                    r.push("</tr>");
                }
            }
            else {
                r.push("<tr><td></td></tr>");
            }
            r.push("</table>");
            return r.join("");
        }
    },

    JSON: function(v) {
        return Ext.encode(v);
    },

    Badge: function(v) {
        if(v) {
            return "<span class='x-display-tag'>" + v + "</span>";
        } else {
            return "";
        }
    }
});

//
Ext.apply(NOC.msg, {
    started: function(message) {
        Ext.toast({
            html: '<div style="text-align: center;"><i class="fa fa-clock-o" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + '</div>',
            align: 'bl',
            bodyStyle: {
                background: '#1E90FF',
                color: 'white',
                "font-weight": 'bold',
//                "font-size": 'large'
            },
            style: {
                background: '#1E90FF'
            },
            listeners: {
                focusenter: function() {
                    this.close();
                }
            },
            width: '50%',
            minHeight: 10,
            paddingY: 0,
            border: false
        });
    },
    complete: function(message) {
        Ext.toast({
            html: '<div style="text-align: center;"><i class="fa fa-check-circle" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + '</div>',
            align: 'bl',
            bodyStyle: {
                background: 'green',
                color: 'white',
                "font-weight": 'bold'
//                "font-size": 'large'
            },
            style: {
                background: 'green'
            },
            listeners: {
                focusenter: function() {
                    this.close();
                }
            },
            width: '50%',
            minHeight: 10,
            paddingY: 0,
            border: false
        });
    },
    failed: function(message) {
        Ext.toast({
            html: '<div style="text-align: center;"><i class="fa fa-bolt" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + '</div>',
            align: 'bl',
            bodyStyle: {
                background: 'red',
                color: 'white',
                "font-weight": 'bold',
//                "font-size": 'large'
            },
            style: {
                background: 'red'
            },
            listeners: {
                focusenter: function() {
                    this.close();
                }
            },
            width: '50%',
            minHeight: 10,
            paddingY: 0,
            border: false
        });
    },
    info: function(message) {
        Ext.toast({
            html: '<div style="text-align: center;"><i class="fa fa-info-circle" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + '</div>',
            align: 'bl',
            bodyStyle: {
                background: '#1E90FF',
                color: 'white',
                "font-weight": 'bold',
//                "font-size": 'large'
            },
            style: {
                background: '#1E90FF'
            },
            listeners: {
                focusenter: function() {
                    this.close();
                }
            },
            width: '50%',
            minHeight: 10,
            paddingY: 0,
            border: false
        });
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
    NOC.msg.failed.apply(this, arguments);
};
//
NOC.info = function(msg) {
    NOC.msg.info.apply(this, arguments);
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
    return (value >= 1 && value <= 4095)
};
//
NOC.is_asn = function(value) {
    return (value > 0)
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
Ext.define("NOC.form.field.VTypes", {
    override: "Ext.form.field.VTypes",

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
            return me.FQDNRe.test(val);
        } catch(e) {
            return false;
        }
    },
    FQDNRe: /^([a-z0-9\-]+\.)+[a-z0-9\-]+$/i,
    FQDNText: "Not valid FQDN",

    // AS-set check
    ASSET: function(val, field){
        var me = this;
        try {
            return me.ASSETRe.test(val);
        } catch(e) {
            return false;
        }
    },   
    ASSETRe: /^AS(-\w+)+$/i,
    ASSETText: "Not valid ASSET, must be in form AS-SET or AS-MEGA-SET",

    // AS/AS-set check
    ASorASSET: function(val, field){
        var me = this;
        return me.ASN(val, field) || me.ASSET(val, field);
    },
    ASorASSETText: "Not valid AS or ASSET, must be in form AS3505, AS-SET, AS-MEGA-SET or AS3245:AS-TEST",

    // Color check
    color: function(val, field) {
        var me = this;
        return me.colorRe.test(val);
    },
    colorRe: /^[0-9a-f]{6}$/i,
    colorText: "Invalid color, must be 6 hexadecimals",

    password: function(val, field) {
        if(field.peerField) {
            var form = field.up("form"),
                peer = form.getForm().findField(field.peerField);
            return (val === peer.getValue());
        }
        return true;
    },
    passwordText: "Passwords do not match",

    json: function(val, field) {
        try {
            Ext.decode(val);
            return true
        }
        catch(err) {
            return false;
        }
    },
    jsonText: "Invalid JSON",

    // Color check
    handler: function(val, field) {
        var me = this;
        return me.handlerRe.test(val);
    },
    handlerRe: /^noc(\.[a-zA-Z_][a-zA-Z0-9_]*)+$/,
    handlerText: "Invalid handler format"
});

//
// UI Styles
// Predefined set of size and settings.
// Applied to field as uiStyle property
//
NOC.uiStyles = {
    // 3 letters
    small: {
        width: 50,
        anchor: null
    },
    // 20 letters
    medium: {
        width: 155,
        anchor: null
    },
    // 40 letters
    large: {
        width: 310,
        anchor: null
    },
    // Full width
    extra: {
        anchor: "100%"
    }
};
