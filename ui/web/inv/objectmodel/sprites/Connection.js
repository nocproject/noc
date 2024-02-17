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
    alias: "sprite.cross_connection",
    inheritableStatics: {
        def: {
            processors: {
                path: "string",
                inputId: "string",
                outputId: "string",
                isSelected: "bool",
                toXY: "data",
                scaleFactor: "number",
            },
            triggers: {
                path: "recalculate",
                inputId: "recalculate",
                outputId: "recalculate",
                isSelected: "recalculate",
                toXY: "recalculate",
                scaleFactor: "recalculate",
            },
            defaults: {
            },
            updaters: {
                recalculate: function(attr) {
                    var me = this;

                    me.createSprites(attr);
                    me.line.setAttributes({
                        strokeStyle: attr.isSelected ? me.getSelectedColor() : me.getAvailableColor(),
                        lineWidth: attr.isSelected ? 4 : 2,
                    });
                },
            },
        },
    },
    config: {
        availableColor: "#1F6D91",
        newColor: "lightgreen",
        disabledColor: "#d0d0d0",
        selectedColor: "#f5d63c",
    },
    hitTest: function(point, options) {
        // Removed the isVisible check since pin will always be visible.
        var me = this,
            x = point[0],
            y = point[1];
        if(me.line.isPointOnPath(x, y)) {
            return me;
        }
        return null;
    },
    createSprites: function(attr) {
        var me = this;

        if(!me.line) {
            me.inputId = attr.inputId;
            me.outputId = attr.outputId;
            me.line = me.add({
                type: "path",
                path: attr.path,
                strokeStyle: me.getAvailableColor(),
                lineWidth: 2,
            });
            me.add(me.getMarker("arrow", attr.toXY, attr.scaleFactor));
        }
    },
    getMarker: function(id, pointXY, scale) {
        var length = 20 * (scale || 1),
            width = 5.5 * (scale || 1),
            path = Ext.String.format("M{0},{1} L{2},{3} L{4},{5} Z",
                pointXY[0], pointXY[1],
                pointXY[0] - length, pointXY[1] + width,
                pointXY[0] - length, pointXY[1] - width
            );

        return {
            type: "path",
            id: id,
            fillStyle: "red",
            path: path,
            hidden: false,
        };
    },
});