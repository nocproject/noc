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
            sc,
            n = name.replace("/", ".");
        sc = me.shapes[name];
        if (sc) {
            return sc;
        }
        sc = joint.shapes.basic.Generic.extend({
            markup: '<g class="rotatable"><g class="scalable"><image/></g><text/></g>',
            defaults: joint.util.deepSupplement({
                //type: "basic." + n,
                type: "basic.Generic.nocobject",
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
                        fill: 'black',
                        ref: 'image',
                        'ref-x':.5,
                        'text-anchor': 'middle',
                        'ref-y':.99
                    }
                }
            }, joint.shapes.basic.Generic.prototype.defaults),
            setFilter: function(filter) {
                var me = this;
                me.attr("image/filter", "url(#" + filter + ")");
            }
        });
        me.shapes[name] = sc;
        return sc;
    }
});
