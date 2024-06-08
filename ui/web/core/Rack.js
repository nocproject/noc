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
  TEXT_PADDING_HORIZONTAL: 2,
  TEXT_PADDING_VERTICAL: 4,
  LABEL_FONT: "10px normal",
  UINIT_FONT: "9px normal lighter",
  EXTERNAL_BOX_FILL: "#2c3e50",
  EXTERNAL_BOX_STROKE_WIDTH: 2,
  RACK_LABEL_FILL: "#e0e0e0",
  UNIT_LABEL_FILL: "#e0e0e0",
  UNIT_RULE_FILL: "#606060",
  UNIT_RULE_STROKE: "#e0e0e0",
  FREE_COLOR: "#7f8c8d",
  NEAR_COLOR: "#f0f0f0",
  FAR_COLOR: "#bdc3c7",
  STROKE_COLOR: "black",
  TEXT_ANCHOR: "end",

  getRack: function(app, x, y, opts, content, side){
    var me = this, rear, front, acc,
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
      far_side = side === "f" ? "r" : "f",
      label = opts.label || null,
      verticalPositionText = function(pos){
        return n_bottom - pos * me.U_HEIGH - me.U_HEIGH / 2 + me.TEXT_PADDING_VERTICAL;
      };
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
      stroke: me.STROKE_COLOR,
      fill: me.EXTERNAL_BOX_FILL,
      "stroke-width": me.EXTERNAL_BOX_STROKE_WIDTH,
    });
    // Internal box
    out.push({
      type: "rect",
      x: x + me.SIDE_WIDTH,
      y: y + me.TOP_WIDTH,
      width: i_width,
      height: i_height,
      stroke: me.STROKE_COLOR,
      fill: me.FREE_COLOR,
    });
    // Unit numbers
    out.push({
      type: "rect",
      x: n_left,
      y: y + me.TOP_WIDTH,
      width: me.N_WIDTH,
      height: i_height,
      stroke: me.STROKE_COLOR,
      fill: me.UNIT_RULE_FILL,
    });

    for(var position = 1; position <= opts.units; position++){
      out.push({
        type: "text",
        x: n_left + me.N_WIDTH - me.TEXT_PADDING_HORIZONTAL,
        y: verticalPositionText(position - 1),
        text: "" + position,
        fill: me.UNIT_LABEL_FILL,
        font: me.LABEL_FONT,
        "text-anchor": me.TEXT_ANCHOR,
      });
      // Unit rulers
      out.push({
        type: "path",
        path: "M" + (x + me.SIDE_WIDTH) + " " + (y + me.TOP_WIDTH + position * me.U_HEIGH) + "h" + (i_width + me.N_WIDTH),
        stroke: me.UNIT_RULE_STROKE,
      });
    }
    /*
         * Content
         */
    rear = content.filter(function(dev){
      return dev.side === "r";
    });
    front = content.filter(function(dev){
      return dev.side === "f";
    });
    acc = side === "r" ? front.concat(rear) : rear.concat(front);
    Ext.each(acc, function(device){
      var shift = Math.round(me.U_HEIGH * device.shift / 3);

      var rect = {
        type: "rect",
        x: x + me.SIDE_WIDTH,
        y: n_bottom - (device.pos + device.units - 1) * me.U_HEIGH - shift,
        width: i_width,
        height: device.units * me.U_HEIGH,
        stroke: me.STROKE_COLOR,
        managed_object_id: device.managed_object_id,
      };
      // Far side
      if(device.side === far_side){
        rect.fill = me.FAR_COLOR;
      }
      // Near side
      if(device.side === side){
        rect.fill = me.NEAR_COLOR
      }

      out.push(rect);
      out.push({
        type: "text",
        text: device.name,
        x: x + me.SIDE_WIDTH + i_width - me.TEXT_PADDING_HORIZONTAL,
        y: verticalPositionText(device.pos - 1) - shift,
        stroke: me.STROKE_COLOR,
        font: me.UINIT_FONT,
        "text-anchor": me.TEXT_ANCHOR,
        managed_object_id: device.managed_object_id,
      });
    });
    // Rack label
    if(label){
      out.push({
        type: "text",
        text: __("Rack: ") + label,
        x: x + e_width - me.TEXT_PADDING_HORIZONTAL - me.SIDE_WIDTH,
        y: y + me.U_HEIGH - me.TEXT_PADDING_VERTICAL,
        fill: me.RACK_LABEL_FILL,
        font: me.LABEL_FONT,
        "text-anchor": me.TEXT_ANCHOR,
      });
    }
    return{sprites: out, height: e_height+me.U_HEIGH};
  },
});
