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
        var view = this.getView();
        view.up('[itemId=sa-managedobject]').getController().setFormTitle(__("Clone") + " {0}", __("CLONE"));
        view.getForm().setValues({bi_id: null});
        view.recordId = undefined;
        // view.down('[itemId=cloneBtn]').setDisabled(true);
        Ext.Array.each(view.query('[itemId$=-inline]'), function(grid) {return grid.getStore().cloneData()});
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
        record.set("id", this.getView().recordId);
        if(this.getView().recordId) {
            record.phantom = false;
            record.proxy.url += record.id + "/";
        }

        this.getView().mask(__("Saving ..."));
        this.getView().saveInlines(record.id,
            Ext.Array.map(this.getView().query('[itemId$=-inline]'), function(grid) {return grid.getStore()}));
        Ext.Object.each(data, function(key, value) {if(!Ext.isEmpty(value)) record.set(key, value)});
        record.save({
            success: function(record, operation) {
                me.getView().unmask();
                me.getView().setHistoryHash();
                me.toMain();
                NOC.msg.complete(__("Saved"));
            },
            failure: function(record, operation) {
                var message = "Error saving record";
                if(operation && operation.error && operation.error.response && operation.error.response.responseText) {
                    var response = Ext.decode(operation.error.response.responseText);
                    if(response && response.message) {
                        message = response.message;
                    }
                }
                NOC.error(message);
                me.getView().unmask();
            },
        });
    },
    // Workaround labelField
    onChange: Ext.emptyFn,
});