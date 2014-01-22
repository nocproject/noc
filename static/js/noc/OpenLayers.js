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
