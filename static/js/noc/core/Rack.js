//---------------------------------------------------------------------
// NOC.core.Rack
// Render SVG rack image
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.Rack");

Ext.define("NOC.core.Rack", {
    singleton: true,

    SIDE_WIDTH: 10,
    BOTTOM_WIDTH: 10,
    TOP_WIDTH: 20,
    SCALE: 2,
    U_HEIGH: 14,
    N_WIDTH: 20,
    TEXT_PADDING: 2,
    N_FONT: "8px monospace",

    getRack: function(x, y, opts) {
        var me = this,
            out = [],
            // Internal width
            i_width = Math.round(opts.width / me.SCALE),
            // Internal height
            i_height = opts.units * me.U_HEIGH,
            // External width
            e_width = i_width + 2 * me.SIDE_WIDTH + me.N_WIDTH;
            // External height
            e_height = i_height + me.BOTTOM_WIDTH + me.TOP_WIDTH;
            // Number boxes left side
            n_left = x + me.SIDE_WIDTH + i_width;
            // Number boxes bottom
            n_bottom = y + me.TOP_WIDTH + i_height;

        // Unit numbers
        for(var u = 1; u <= opts.units; u++) {
            out.push({
                type: "rect",
                x: n_left,
                y: n_bottom - u * me.U_HEIGH,
                width: me.N_WIDTH,
                height: me.U_HEIGH,
                stroke: "#808080"
            });
            out.push({
                type: "text",
                x: n_left + me.TEXT_PADDING,
                y: n_bottom - (u - 1) * me.U_HEIGH - me.TEXT_PADDING,
                text: "" + u,
                fill: "black",
                font: me.N_FONT
            });
        }
        // External box
        out.push({
            type: "rect",
            x: x,
            y: y,
            width: e_width,
            height: e_height,
            stroke: "black",
            "stroke-width": 2
        });
        // Internal box
        out.push({
            type: "rect",
            x: x + me.SIDE_WIDTH,
            y: y + me.TOP_WIDTH,
            width: i_width,
            height: i_height,
            stroke: "black",
            fill: "#C0C0C0"
        });
        return out;
    }
});
