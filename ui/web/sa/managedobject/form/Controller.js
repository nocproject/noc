//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.managedobject.form.Controller');
Ext.define('NOC.sa.managedobject.form.Controller', {
    extend: 'Ext.app.ViewController',
    requires: [
        "Ext.ux.grid.column.GlyphAction",
        "NOC.sa.managedobject.Model",
        "NOC.sa.managedobject.Proxy",
    ],
    alias: 'controller.managedobject.form',

    toMain: function() {
        var mainView = this.getView().up().up();
        mainView.setActiveItem('managedobject-select');
        mainView.setHistoryHash();
    },
    onSaveRecord: function() {
        console.log('click save!');
        var me = this.getView();
        if(!me.form.isValid()) {
            NOC.error(__("Error in data"));
            return;
        }
        var v = me.getFormData();
        // ToDo remove id, when new record
        // if(!me.currentRecord && v[me.idField] !== undefined) {
        //     delete v[me.idField];
        // }
        //
        this.saveRecord(v);

    },
    onNewRecord: function() {
        console.log('form handler : onNewRecord');
    },
    onCloneRecord: function() {

    },
    saveRecord: function(data) {
        var me = this,
            record = Ext.create("NOC.sa.managedobject.Model");

        record.self.setProxy({type: "managedobject"});
        if(!record.validate().isValid()) {
            // @todo: Error report
            NOC.error(__("Invalid data!"));
            return;
        }
        if(this.getView().recordId) {
            record.set("id", this.getView().recordId);
            record.phantom = false;
            record.proxy.url = record.proxy.url.replace("{{id}}", record.id);
        }

        this.getView().mask(__("Saving ..."));
        this.getView().saveInlines(record.id,
            Ext.Array.map(this.getView().query('[itemId$=-inline]'), function(grid) {return grid.getStore()}));
        Ext.Object.each(data, function(key, value) {if(!Ext.isEmpty(value)) record.set(key, value)});
        var result = record.save({
            success: function(record, operation) {
                me.getView().unmask();
                NOC.msg.complete(__("Saved"));
            },
            failure: function(record, operation) {
                var message = "Error saving record";
                NOC.error(message);
                me.getView().unmask();
            },
        });
    },
    onChange: Ext.emptyFn,
});