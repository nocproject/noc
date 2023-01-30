//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.managedobject.form.Controller');
Ext.define('NOC.sa.managedobject.form.Controller', {
    extend: 'Ext.app.ViewController',
    requires: [
        "Ext.ux.grid.column.GlyphAction"
    ],
    alias: 'controller.managedobject.form',

    toMain: function() {
        // var mainView = this.getView().up('[itemId=sa.managedobject]');
        // var mainView = Ext.ComponentQuery.query('[itemId=sa-managedobject]')[0];
        var mainView = this.getView().up().up();
        mainView.setActiveItem('managedobject-select');
        this.getView().up().up().setActiveItem('managedobject-select');
        mainView.setHistoryHash();
    },
    onChange: Ext.emptyFn,
});