//---------------------------------------------------------------------
// NOC.core.Rack
// Render SVG conduits image
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Conduits");

Ext.define("NOC.core.Conduits", {
    singleton: true,
    //
    defaultStroke: "black",
    defaultFillColor: "white",
    brokenFillColor: "#c0c0c0",
    //
    getConduits: function(data, scale) {
        var me = this,
            out = [];
        scale = scale || 1;
        Ext.each(data, function(v) {
            out.push({
                type: "circle",
                radius: v.d / 2 / scale,
                x: v.x / scale,
                y: v.y / scale,
                stroke: me.defaultStroke,
                "stroke-width": 2,
                fill: v.status ? me.defaultFillColor : me.brokenFillColor
            });
            out.push({
                type: "text",
                x: v.x / scale,
                y: v.y / scale,
                text: "" + v.n,
                stroke: me.defaultStroke
            });
        });
        return out;
    },
    // Generate conduits block
    getBlock: function(opts) {
        var count = opts.count || 0,
            d = opts.d || 100,
            start = opts.start || 1,
            w = opts.w || 0,
            out = [],
            rows = Math.ceil(count / w),
            y0 = d * rows,
            n;
        for(var i = 0; i < count; i++) {
            n = start + i;
            out.push({
                n: n,
                x: (1 + i % w) * d,
                y: y0 - Math.floor(i / w) * d,
                d: d,
                status: true
            });
        }
        return out;
    }
});