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
    SCALE: 3,
    U_HEIGH: 15,
    N_WIDTH: 14,
    TEXT_PADDING: 2,
    N_FONT: "10px normal",
    B_FONT: "10px normal",
    FREE_COLOR: "#808080",
    NEAR_COLOR: "#f0f0f0",
    FAR_COLOR: "#d0d0d0",

    getRack: function(x, y, opts, content, side) {
        var me = this,
            out = [],
            // Internal width
            i_width = Math.round(opts.width / me.SCALE),
            // Internal height
            i_height = opts.units * me.U_HEIGH,
            // External width
            e_width = i_width + 2 * me.SIDE_WIDTH + me.N_WIDTH,
            // External height
            e_height = i_height + me.BOTTOM_WIDTH + me.TOP_WIDTH,
            // Number boxes left side
            n_left = x + me.SIDE_WIDTH + i_width,
            // Number boxes bottom
            n_bottom = y + me.TOP_WIDTH + i_height,
            // far side
            far_side = side === "f" ? "r" : "f";
        /*
         * Enclosure
         */

        // External box
        out.push({
            type: "rect",
            x: x,
            y: y,
            width: e_width,
            height: e_height,
            stroke: "black",
            fill: "#444444",
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
            fill: me.FREE_COLOR
        });
        // Unit numbers
        out.push({
            type: "rect",
            x: n_left,
            y: y + me.TOP_WIDTH,
            width: me.N_WIDTH,
            height: i_height,
            stroke: "black",
            fill: "#606060"
        });

        for(var u = 1; u <= opts.units; u++) {
            out.push({
                type: "text",
                x: n_left + me.TEXT_PADDING,
                y: n_bottom - (u - 1) * me.U_HEIGH - me.U_HEIGH / 2,
                text: "" + u,
                fill: "#e0e0e0",
                font: me.N_FONT
            });
        }
        // Unit rulers
        for(var u = 1; u < opts.units; u++) {
            out.push({
                type: "path",
                path: "M" + (x + me.SIDE_WIDTH) + " " + (y + me.TOP_WIDTH + u * me.U_HEIGH) + "h" + (i_width + me.N_WIDTH),
                stroke: "#e0e0e0"
            });
        }
        /*
         * Content
         */
        // Far side
        for(var i in content) {
            var c = content[i], shift;
            if(c.side !== far_side) {
                continue;
            }
            shift = Math.round(me.U_HEIGH * c.shift / 3);
            out.push({
                type: "rect",
                x: x + me.SIDE_WIDTH,
                y: n_bottom - (c.pos + c.units - 1)* me.U_HEIGH - shift,
                width: i_width,
                height: c.units * me.U_HEIGH,
                stroke: "black",
                fill: me.FAR_COLOR
            });
            out.push({
                type: "text",
                text: c.name,
                x: x + me.SIDE_WIDTH + 10,
                y: n_bottom - (c.pos + c.units / 2 - 1)* me.U_HEIGH - shift,
                stroke: "black",
                font: me.B_FONT
            });
        }
        // Near side
        for(var i in content) {
            var c = content[i], shift;
            if(c.side !== side) {
                continue;
            }
            shift = Math.round(me.U_HEIGH * c.shift / 3);
            out.push({
                type: "rect",
                x: x + me.SIDE_WIDTH,
                y: n_bottom - (c.pos + c.units - 1)* me.U_HEIGH - shift,
                width: i_width,
                height: c.units * me.U_HEIGH,
                stroke: "black",
                fill: me.NEAR_COLOR
            });
            out.push({
                type: "text",
                text: c.name,
                x: x + me.SIDE_WIDTH + 10,
                y: n_bottom - (c.pos + c.units / 2 - 1)* me.U_HEIGH - shift,
                stroke: "black",
                font: me.B_FONT
            });
        }
        return out;
    }
});
