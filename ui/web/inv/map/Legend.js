//---------------------------------------------------------------------
// Map Legend
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.Legend");

Ext.define("NOC.inv.map.Legend", {
  extend: "Ext.panel.Panel",
  alias: "widget.legend",

  items: [
    {
      xtype: "box",
      padding: "0 5",
      html: __("Legend"),
    },
    {
      xtype: "draw",
      fontSize: 15,
      height: 338,
      sprites: [
        {
          type: "text", x: 10, y: 15,
          text: __("Object status style"),
        },
        {
          type: "rect", x: 20, y: 22, width: 20, height: 10,
          fillStyle: "#7f8c8d",
        },
        {
          type: "text", x: 60, y: 30,
          text: __("unknown"),
        },
        {
          type: "rect", x: 20, y: 37, width: 20, height: 10,
          fillStyle: "#23cc71",
        },
        {
          type: "text", x: 60, y: 45,
          text: "Ok",
        },
        {
          type: "rect", x: 20, y: 52, width: 20, height: 10,
          fillStyle: "#f1c40f",
        },
        {
          type: "text", x: 60, y: 60,
          text: "alarm",
        },
        {
          type: "rect", x: 20, y: 67, width: 20, height: 10,
          fillStyle: "#404040",
        },
        {
          type: "text", x: 60, y: 75,
          text: "unreach",
        },
        {
          type: "rect", x: 20, y: 82, width: 20, height: 10,
          fillStyle: "#c0392b",
        },
        {
          type: "text", x: 60, y: 90,
          text: "down",
        },
        {
          type: "text", x: 10, y: 105,
          text: __("Link bandwidth style"),
        },
        {
          type: "line", fromX: 20, fromY: 120, toX: 100, toY: 120,
          lineDash: [10, 5],
          lineWidth: 1,
        },
        {
          type: "text", x: 110, y: 120,
          text: __("data unavailable"),
        },
        {
          type: "line", fromX: 20, fromY: 135, toX: 100, toY: 135,
          lineWidth: 1,
        },
        {
          type: "text", x: 110, y: 135,
          text: "100M",
        },
        {
          type: "line", fromX: 20, fromY: 150, toX: 100, toY: 150,
          lineWidth: 2,
        },
        {
          type: "text", x: 110, y: 150,
          text: "1G",
        },
        {
          type: "line", fromX: 20, fromY: 165, toX: 100, toY: 165,
          lineWidth: 4,
        },
        {
          type: "text", x: 110, y: 165,
          text: "10G",
        },
        {
          type: "text", x: 10, y: 185,
          text: __("Link utilization style"),
        },
        {
          type: "line", fromX: 20, fromY: 200, toX: 100, toY: 200,
          strokeStyle: "#006600",
        },
        {
          type: "text", x: 110, y: 200,
          text: "0%",
        },
        {
          type: "line", fromX: 20, fromY: 215, toX: 100, toY: 215,
          strokeStyle: "#ff9933",
        },
        {
          type: "text", x: 110, y: 215,
          text: "50%",
        },
        {
          type: "line", fromX: 20, fromY: 230, toX: 100, toY: 230,
          strokeStyle: "#990000",
        },
        {
          type: "text", x: 110, y: 230,
          text: "80%",
        },
        {
          type: "line", fromX: 20, fromY: 245, toX: 100, toY: 245,
          strokeStyle: "#ff0000",
        },
        {
          type: "text", x: 110, y: 245,
          text: "95%",
        },
        {
          type: "line", fromX: 20, fromY: 260, toX: 100, toY: 260,
          strokeStyle: "#ff9933",
        },
        {
          type: "text", x: 40, y: 262,
          fontFamily: "FontAwesome", fontSize: 5,
          fillStyle: "#ff9933",
          text: __("\uf111"),
        },
        {
          type: "text", x: 110, y: 260,
          text: __("balance"),
        },
        {
          type: "text", x: 10, y: 280,
          text: __("Link status style"),
        },
        {
          type: "line", fromX: 20, fromY: 295, toX: 100, toY: 295,
          strokeStyle: "#c0392b",
        },
        {
          type: "text", x: 40, y: 298,
          fontFamily: "FontAwesome", fontSize: 12,
          fillStyle: "#c0392b",
          text: __("\uf071"),
        },
        {
          type: "text", x: 110, y: 295,
          text: __("oper down"),
        },
        {
          type: "line", fromX: 20, fromY: 310, toX: 100, toY: 310,
          strokeStyle: "#7f8c8d",
        },
        {
          type: "text", x: 40, y: 314,
          fontFamily: "FontAwesome", fontSize: 12,
          fillStyle: "#7f8c8d",
          text: __("\uf00d"),
        },
        {
          type: "text", x: 110, y: 310,
          text: __("admin down"),
        },
        {
          type: "line", fromX: 20, fromY: 325, toX: 100, toY: 325,
          strokeStyle: "#8e44ad",
        },
        {
          type: "text", x: 40, y: 329,
          fontFamily: "FontAwesome", fontSize: 12,
          fillStyle: "#8e44ad",
          text: __("\uf05e"),
        },
        {
          type: "text", x: 110, y: 325,
          text: __("STP blocked"),
        },
      ],
    },
  ],
});
