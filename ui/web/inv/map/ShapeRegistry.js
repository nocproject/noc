//---------------------------------------------------------------------
// JointJS shape registry
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.ShapeRegistry");

Ext.define("NOC.inv.map.ShapeRegistry", {
    singleton: true,
    shapes: {},

    getShape: function (name) {
        var me = this,
            sc, sv,
            n = name.replace("/", ".").replace(" ", "_"),
            typeName = "noc." + n,
            registerClass = function (name, cls) {
                var sr = joint.shapes,
                    tns = name.split(".").reverse(),
                    v;
                for (;;) {
                    v = tns.pop();
                    if (tns.length) {
                        if (sr[v] === undefined) {
                            sr[v] = {};
                        }
                        sr = sr[v];
                    } else {
                        sr[v] = cls;
                        break;
                    }
                }
            };

        sc = me.shapes[name];
        if (sc) {
            return sc;
        }
        // Shape class
        sc = joint.shapes.basic.Generic.extend({
            markup: '<g class="rotatable"><g class="scalable"><image/></g><text/></g>',
            defaults: joint.util.deepSupplement({
                //type: "basic." + n,
                type: typeName,
                size: {
                    width: 50,
                    height: 50
                },
                attrs: {
                    image: {
                        'width': 50,
                        'height': 50,
                        'xlink:href': "/inv/map/stencils/" + name + "/"
                    },
                    text: {
                        text: 'New Object',
                        fill: '#000000',
                        ref: 'image',
                        'ref-x': .5,
                        'text-anchor': 'middle',
                        'ref-y': .99
                    }
                }
            }, joint.shapes.basic.Generic.prototype.defaults),
            setFilter: function (filter) {
                var me = this;
                me.attr("image/filter", "url(#" + filter + ")");
            }
        });
        me.shapes[name] = sc;
        registerClass(typeName, sc);
        // Shape view
        sv = joint.dia.ElementView.extend({
            getStrokeBBox: function(el) {
                el = el || V(this.el).find("image")[0].node;
                return joint.dia.ElementView.prototype.getStrokeBBox.apply(this, [el]);
            }
        });
        registerClass(typeName + "View", sv);
        return sc;
    }
});
