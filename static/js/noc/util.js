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
    //true: "<img src='/static/pkg/famfamfam-silk/tick.png' />",
    true: "<i class='icon-ok'></i>",
    false: "<i class='icon-remove'></i>",
    null: "<i class='icon-circle-blank'></i>",
};

//
// NOC.render.Bool(v)
//     Grid field renderer for boolean values
//     Displays icons depending on true/false status
//
NOC.render.Bool = function(v) {
    return _noc_bool_img[v];
}

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
            return "<span class='x-boxselect-item'>" + x + "</span>";
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
        var me = this;
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
            // Update element
            el.update("<pre class='sh_sourcecode'>" + html + "</pre>");
        });
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
