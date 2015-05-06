//---------------------------------------------------------------------
// OpenLayers extension
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.log("Loading NOC's OpenLayer extensions");

OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
    defaultHandlerOptions: {
        single: true,
        double: false,
        pixelTolerance: 0,
        stopSingle: false,
        stopDouble: false
    },
    initialize: function(options) {
        this.handlerOptions = OpenLayers.Util.extend(
            {}, this.defaultHandlerOptions);
        OpenLayers.Control.prototype.initialize.apply(this, arguments);
        this.handler = new OpenLayers.Handler.Click(
            this, {
                click: Ext.bind(options.fn, options.scope || this)
            }, this.handlerOptions
        );
    }
});

// Renderer symbols
OpenLayers.Renderer.symbol.diamond = [-5,0, 0,5, 5,0, 0,-5];
OpenLayers.Renderer.symbol.antenna = [
    7, 7, 7, 15, 9, 15, 9, 7,
    15, 0, 14, 0, 9, 5,
    9, 0, 7, 0, 7, 5,
    1, 0, 0, 0, 7, 7];
OpenLayers.Renderer.symbol.flag = [
    0, 0, 0, 15, 1, 15, 1, 10,
    15, 10, 15, 1, 1, 1, 1, 0, 0, 0
];
