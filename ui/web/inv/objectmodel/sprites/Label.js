//---------------------------------------------------------------------
// NOC.inv.objectmodel.sprites.Label
// Render SVG pin image
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.sprites.Label");

Ext.define("NOC.inv.objectmodel.sprites.Label", {
    extend: "Ext.draw.sprite.Composite",
    alias: "sprite.pin",
    inheritableStatics: {
        def: {
            processors: {
            },
            triggers: {
            },
            defaults: {
            },
            updaters: {
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
    createSprites: function() {
        var me = this;
    },
});