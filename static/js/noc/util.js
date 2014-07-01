//----------------------------------------------------------------------
// Various javascript utilities
//----------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

// NOC namespace
Ext.namespace("NOC", "NOC.render");
//
// NOC.render.Bool(v)
//     Grid field renderer for boolean values
//     Displays icons depending on true/false status
//
NOC.render.Bool = function(v) {
    return {
        true: "<i class='fa fa-check' style='color:" + NOC.colors.yes + "'></i>",
        false: "<i class='fa fa-times' style='color:" + NOC.colors.no + "'></i>",
        null: "<i class='fa fa-circle-o'></i>"
    }[v];
};

//
// NOC.render.URL(v)
//      Grid field renderer for URLs
//
NOC.render.URL = function(v) {
    return "<a href =' " + v + "' target='_'>" + v + "</a>";
}

//
// NOC.render.Tags(v)
//      Grid field renderer for tags
//
NOC.render.Tags = function(v) {
    if(v) {
        return v.map(function(x) {
            return "<span class='x-display-tag'>" + x + "</span>";
        }).join(" ");
    } else {
        return "";
    }
}

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

NOC.render.Clickable = function(value) {
    return "<a href='#' class='noc-clickable-cell'>" + value + "</a>";
};

NOC.render.ClickableLookup = function(name) {
    var l = name + "__label";
    return function(value, meta, record) {
        var v = value ? record.get(l) : "...";
        return "<a href='#' class='noc-clickable-cell' title='Click to change...'>" + v + "</a>";
    };
};

NOC.render.WrapColumn = function (val){
    return '<div style="white-space:normal !important;">'+ val +'</div>';
};

NOC.render.Date = function(val) {
    if(!val) {
        return "";
    }
    return Ext.Date.format(val, "Y-m-d")
};

NOC.render.DateTime = function(val) {
    if(!val) {
        return "";
    }
    return Ext.Date.format(val, "Y-m-d H:i:s")
};

NOC.render.Choices = function(choices) {
    return function(value) {
        return choices[value];
    }
};

NOC.render.Timestamp = function(val) {
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
        }
    return "" + y + "-" + f(m) + "-" + f(D) + " " +
        f(h) + ":" + f(M) + ":" + f(s);
};

NOC.render.Duration = function(val) {
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
};

NOC.render.Size = function(v) {
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
}

NOC.render.Join = function(sep) {
    return function(value) {
        return value.join(sep);
    }
}

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
// SHJS wrapper
//
Ext.define("NOC.SyntaxHighlight", {
    singleton: true,
    langCache: {},
    withLang: function(lang, callback) {
        var me = this;
        if(lang in me.langCache) {
            Ext.callback(callback, me, [me.langCache[lang]]);
        } else {
            Ext.Ajax.request({
                url: "/static/js/highlight/" + lang + ".js",
                scope: me,
                success: function(response) {
                    // Override SHJS's global scope
                    with(this) {
                        this.sh_languages = {};
                        eval(response.responseText);
                        me.langCache[lang] = this.sh_languages[lang];
                    }
                    Ext.callback(callback, me, [me.langCache[lang]]);
                }
            });
        }
    },
    highlight: function(el, text, lang) {
        var me = this,
            showNumbers = lang != "diff",
            updateEl = function(el, html) {
                var out = [];
                // Append line numbers, if required
                if(showNumbers) {
                    var l = html.match(/\n/g).length;
                    out.push("<div class='noc-numbers'>");
                    for(var i = 1; i <= l; i++) {
                        out.push(i + "<br/>");
                    }
                    out.push("</div>");
                }
                // Append code
                out = out.concat(["<pre class='sh_sourcecode'>", html, "</pre>"]);
                // Update element
                el.update(out.join(""));
            };
        if(lang) {
            me.withLang(lang, function(l) {
                var tags = sh_highlightString(text, l);
                //
                // Fill text nodes
                var last = undefined;
                for(var i in tags) {
                    var t = tags[i];
                    if(last) {
                        last.end = t.pos;
                    }
                    last = t;
                }
                // Generate HTML
                var html = tags.map(function(v) {
                    var t = text.substr(v.pos, v.end - v.pos);
                    if(v.node) {
                        return "<span class='" + v.node.className + "'>" +
                            t + "</span>";
                    } else {
                        return t;
                    }
                }).join("");
                updateEl(el, html);
            });
        } else {
            updateEl(el, text);
        }
    }
});
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
// custom Vtype for vtype:"VlanID"
Ext.apply(Ext.form.field.VTypes, {
    VlanID: function(val, field) {
        try {
            var id = parseInt(field.getValue());
            return NOC.is_vlanid(id);
        } catch(e) {
            return false;
        }
    },
    VlanIDText: "Must be a numeric value [1-4095]",
    VlanIDMask: /[\d\/]/
});
//
// custom Vtype for vtype:"ASN" - autonomous system number
Ext.apply(Ext.form.field.VTypes, {
    ASN: function(val, field) {
        try {
            var asn = parseInt(field.getValue());
            return NOC.is_asn(asn);
        } catch(e) {
            return false;
        }
    },
    ASNText: "AS num must be a numeric value > 0",
    ASNMask: /[\d\/]/
});
//
// custom Vtype for vtype:"IPv4"
Ext.apply(Ext.form.field.VTypes, {
    IPv4: function(val, field){
        try {
            var ipv4 = field.getValue();
            return NOC.is_ipv4(ipv4);
        } catch(e) {
            return false;
        }
    },
    IPv4Text: "Must be a numeric value 0.0.0.0 - 255.255.255.255",
    IPv4Mask: /[\d\.]/i
});
//
// custom Vtype for vtype:"IPv4Prefix"
Ext.apply(Ext.form.field.VTypes, {
    IPv4Prefix: function(val, field){
        try {
            var ipv4pref = field.getValue();
            return NOC.is_ipv4_prefix(ipv4pref);
        } catch(e) {
            return false;
        }
    },
    IPv4PrefixText: "Must be a numeric value 0.0.0.0/0 - 255.255.255.255/32",
    IPv4PrefixMask: /[\d\.\/]/i
});
//
// custom Vtype for vtype:"FQDN"
Ext.apply(Ext.form.field.VTypes, {
    FQDN: function(val, field){
        try {
            var fqdntest = /^([a-z0-9\-]+\.)+[a-z0-9\-]+$/i;
            var fqdn = field.getValue();
            return fqdntest.test(fqdn);
        } catch(e) {
            return false;
        }
    },
    FQDNText: "Not valid FQDN",
    FQDNMask: /[-.a-zA-Z0-9]/i
});
//
// custom Vtype for vtype:"ASSET"
Ext.apply(Ext.form.field.VTypes, {
    ASSET: function(val, field){ 
        try {
            var assettest = /^AS(-\w+)+$/i;
            var asset = field.getValue();
            return assettest.test(asset); 
        } catch(e) {
            return false;
        }
    },   
    ASSETText: "Not valid ASSET, must be in form AS-SET or AS-MEGA-SET",
    ASSETMask: /[A-Z0-9-]/i
});
//
// custom Vtype for vtype:"ASorASSET"
Ext.apply(Ext.form.field.VTypes, {
    ASorASSET: function(val, field){
        try {
            var asorassettest = /^(AS(\d+|(-\w+)+)(:\S+)?(\s+AS(\d+|(-\w+)+)(:\S+)?)*$)/i;
            var asorasset = field.getValue();
            return asorassettest.test(asorasset);
        } catch(e) {
            return false;
        }
    },
    ASorASSETText: "Not valid AS or ASSET, must be in form AS3505, AS-SET, AS-MEGA-SET or AS3245:AS-TEST",
    ASorASSETMask: /[A-Z0-9-:]/i
});
//
// Override grid column state ids
//
Ext.override(Ext.grid.column.Column, {
    getStateId: function() {
        return this.stateId || this.dataIndex || this.headerId;
    }
});
//
// Override form field labels
//
Ext.override(Ext.form.Panel, {
    initComponent: function() {
        var me = this,
            applyLabelStyle = function(field) {
                if((field.xtype == "fieldset") || (field.xtype == "container")) {
                    Ext.each(field.items.items, function(f) {
                        applyLabelStyle(f);
                    });
                } else {
                    if(!field.allowBlank) {
                        field.labelClsExtra = "noc-label-required";
                    }
                }
            };
        me.on("beforeadd", function(form, field) {
            applyLabelStyle(field);
        });
        me.callParent();
    }
});

Ext.override(Ext.tree.Column, {
    cellTpl: [
        '<tpl for="lines">',
        '<img src="{parent.blankUrl}" class="{parent.childCls} {parent.elbowCls}-img ',
        '{parent.elbowCls}-<tpl if=".">line<tpl else>empty</tpl>" role="presentation"/>',
        '</tpl>',


        '<img src="{blankUrl}" class="{childCls} {elbowCls}-img {elbowCls}',
        '<tpl if="isLast">-end</tpl><tpl if="expandable">-plus {expanderCls}</tpl>" role="presentation"/>',
        '<tpl if="checked !== null">',
        '<input type="button" {ariaCellCheckboxAttr}',
        ' class="{childCls} {checkboxCls}<tpl if="checked"> {checkboxCls}-checked</tpl>"/>',
        '</tpl>',


        '<tpl if="glyphCls">' ,
            '<i class="{glyphCls}" style="font-size: 16px"></i> ',
        '<tpl else>',
            '<img src="{blankUrl}" role="presentation" class="{childCls} {baseIconCls} ',
            '{baseIconCls}-<tpl if="leaf">leaf<tpl else>parent</tpl> {iconCls}"',
            '<tpl if="icon">style="background-image:url({icon})"</tpl>/>',
        '</tpl>',
        '<tpl if="href">',
        '<a href="{href}" role="link" target="{hrefTarget}" class="{textCls} {childCls}">{value}</a>',
        '<tpl else>',
        '<span class="{textCls} {childCls}">{value}</span>',
        '</tpl>'
    ],
    initTemplateRendererData: function (value, metaData, record, rowIdx, colIdx, store, view) {
        var me = this,
            renderer = me.origRenderer,
            data = record.data,
            parent = record.parentNode,
            rootVisible = view.rootVisible,
            lines = [],
            parentData,
            iconCls = data.iconCls,
            glyphCls;

        while (parent && (rootVisible || parent.data.depth > 0)) {
            parentData = parent.data;
            lines[rootVisible ? parentData.depth : parentData.depth - 1] =
            parentData.isLast ? 0 : 1;
            parent = parent.parentNode;
        }

        if(iconCls && iconCls.indexOf("fa fa-") == 0) {
            glyphCls = iconCls;
            iconCls = null;
        }

        return {
            record: record,
            baseIconCls: me.iconCls,
            glyphCls: glyphCls,
            iconCls: iconCls,
            icon: data.icon,
            checkboxCls: me.checkboxCls,
            checked: data.checked,
            elbowCls: me.elbowCls,
            expanderCls: me.expanderCls,
            textCls: me.textCls,
            leaf: data.leaf,
            expandable: record.isExpandable(),
            isLast: data.isLast,
            blankUrl: Ext.BLANK_IMAGE_URL,
            href: data.href,
            hrefTarget: data.hrefTarget,
            lines: lines,
            metaData: metaData,
            // subclasses or overrides can implement a getChildCls() method, which can
            // return an extra class to add to all of the cell's child elements (icon,
            // expander, elbow, checkbox).  This is used by the rtl override to add the
            // "x-rtl" class to these elements.
            childCls: me.getChildCls ? me.getChildCls() + ' ' : '',
            value: renderer ? renderer.apply(me.origScope, arguments) : value
        };
    },
    treeRenderer: function(value, metaData, record, rowIdx, colIdx, store, view){
        var me = this,
            cls = record.get('cls'),
            rendererData;

        if (cls) {
            metaData.tdCls += ' ' + cls;
        }
        rendererData = me.initTemplateRendererData(value, metaData, record, rowIdx, colIdx, store, view);

        return me.getTpl('cellTpl').apply(rendererData);
    }
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
