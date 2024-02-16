//---------------------------------------------------------------------
// NOC.inv.objectmodel.sprites.Connection
// Render SVG pin image
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.sprites.Connection");

Ext.define("NOC.inv.objectmodel.sprites.Connection", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.cross.connection",
    inheritableStatics: {
        def: {
            processors: {
                path: "string",
            },
            triggers: {
                path: "recalculate",
            },
            defaults: {
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this;

                    me.createSprites(attr);
                },
            },
        },
    },
    config: {
    },
    hitTest: function(point, options) {
        // Removed the isVisible check since pin will always be visible.
        var me = this,
            x = point[0],
            y = point[1];
    },
    createSprites: function(attr) {
        var me = this;

        if(!me.line) {
            me.line = me.add({
                type: "path",
                path: attr.path,
                strokeStyle: "#2c3e50",
            });
        }
    },
    getMarker: function(id) {
        var point1X = 20,
            point1Y = 7.5,
            path = Ext.String.format("M{0},{1} L{2},{3} L0,0 Z", point1X, point1Y, point1X, (-1) * point1Y);
        return {
            type: "path",
            id: id,
            fillStyle: "red",
            path: path,
            hidden: true,
        };
    },
});