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
        var mainView = this.getView().up('[appId=sa.managedobject]');
        mainView.getLayout().setActiveItem('managedobject-select');
        mainView.setHistoryHash();
    },
    onChange: Ext.emptyFn,
});