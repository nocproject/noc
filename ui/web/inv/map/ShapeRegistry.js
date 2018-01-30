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

    getShape: function(name) {
        var me = this,
            sc, sv,
            n = name.replace("/", ".").replace(" ", "_"),
            typeName = "noc." + n,
            registerClass = function(name, cls) {
                var sr = joint.shapes,
                    tns = name.split(".").reverse(),
                    v;
                for(; ;) {
                    v = tns.pop();
                    if(tns.length) {
                        if(sr[v] === undefined) {
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
        if(sc) {
            return sc;
        }
        // Shape class
        sc = joint.shapes.basic.Generic.extend({
            markup: '<g class="scalable"><image/></g><g class="rotatable"><text filter="url(#solid)"/></g>',
            defaults: joint.util.deepSupplement({
                type: typeName,
                size: {
                    width: 50,
                    height: 50
                },
                attrs: {
                    image: {
                        'width': 50,
                        'height': 50,
                        'xlink:href': "/ui/pkg/stencils/" + name + ".svg"
                    },
                    text: {
                        text: 'New Object',
                        fill: '#000000',
                        ref: 'image',
                        'ref-x': '50%',
                        'ref-dy': 3,
                        'text-anchor': 'middle'
                    }
                }
            }, joint.shapes.basic.Generic.prototype.defaults),
            setFilter: function(filter) {
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
