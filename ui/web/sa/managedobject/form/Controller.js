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
    url: '/sa/managedobject/',

    toMain: function() {
        this.gotoItem('managedobject-select');
    },
    onSaveRecord: function() {
        var me = this.getView();
        if(!this.getView().down('[itemId=managedobject-form-panel]').form.isValid()) {
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
    onSaveRecords: function() {
        var me = this,
            values = {},
            formPanel = this.getView().down('[itemId=managedobject-form-panel]'),
            form = formPanel.getForm(),
            groupEditFields = Ext.Array.filter(form.getFields().items, function(field) {return field.groupEdit}),
            valuesTxt = "";
        // @todo: Form validation
        Ext.Array.each(groupEditFields, function(field) {
            if(Ext.isFunction(field.isDirty) && field.isDirty()) {
                if(Ext.isFunction(field.getDisplayValue) && field.getDisplayValue() !== "Leave unchanged") {
                    valuesTxt = (field.fieldLabel || field.name) + ": '" + field.getDisplayValue() + "'</br>";
                } else if(field.getValue() !== "Leave unchanged") {
                    valuesTxt = (field.fieldLabel || field.name) + ": '" + field.getValue() + "'</br>";
                }
                if(field.getValue() !== "Leave unchanged" || field.getDisplayValue() !== "Leave unchanged") {
                    values[field.name] = field.getValue();
                }
            }
        });
        if(!Ext.Object.isEmpty(values)) {
            values.ids = formPanel.ids;
            var message = Ext.String.format("Do you wish to change {0} record(s): <br/><br/>{1}<br/>This operation cannot be undone!", values.ids.length, valuesTxt);
            Ext.Msg.show({
                title: __("Change records?"),
                msg: message,
                buttons: Ext.Msg.YESNO,
                icon: Ext.window.MessageBox.QUESTION,
                modal: true,
                scope: this,
                fn: function(button) {
                    if(button === "yes") {
                        Ext.Ajax.request({
                            url: "/sa/managedobject/actions/group_edit/",
                            method: "POST",
                            scope: me,
                            jsonData: values,
                            success: function() {
                                NOC.info(__("Records has been updated"));
                                me.getView().setHistoryHash();
                                me.reloadSelectionGrids();
                                me.toMain();
                            },
                            failure: function() {
                                NOC.error(__("Failed"));
                            }
                        });
                    }
                }
            });
        } else {
            me.toMain();
        }
    },
    onNewRecord: function() {
        this.newRecord();
    },
    onCloneRecord: function() {
        var view = this.getView(),
            formPanel = this.getView().down('[itemId=managedobject-form-panel]');
        view.up('[itemId=sa-managedobject]').getController().setFormTitle(__("Clone") + " {0}", "CLONE");
        formPanel.getForm().setValues({bi_id: null});
        formPanel.recordId = undefined;
        Ext.Array.each(view.query('[itemId$=-inline]'), function(grid) {return grid.getStore().cloneData()});
        // view.down('[itemId=cloneBtn]').setDisabled(true);
        view.down('[itemId=createBtn]').setDisabled(true);
        view.down('[itemId=deleteBtn]').setDisabled(true);
    },
    onDeleteRecord: function() {
        var me = this;
        Ext.Msg.show({
            title: __("Delete record?"),
            msg: __("Do you wish to delete record? This operation cannot be undone!"),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if(button == "yes")
                    me.deleteRecord();
            }
        });
    },
    onResetRecord: function() {
        this.getView().getForm().reset();
        this.getView().up('[itemId=sa-managedobject]').getController().resetInlineStore(this.getView());
    },
    onConfig: function() {
        this.itemPreview('sa-config');
    },
    onConfDB: function() {
        this.itemPreview('sa-confdb');
    },
    onCard: function() {
        var formPanel = this.getView().down('[itemId=managedobject-form-panel]');
        if(formPanel.recordId) {
            window.open(
                "/api/card/view/managedobject/" + formPanel.recordId + "/"
            );
        }
    },
    onDashboard: function() {
        var formPanel = this.getView().down('[itemId=managedobject-form-panel]');
        if(formPanel.recordId) {
            window.open(
                "/ui/grafana/dashboard/script/noc.js?dashboard=mo&id=" + formPanel.recordId
            );
        }
    },
    onConsole: function() {
        this.itemPreview('sa-console');
    },
    onScripts: function() {
        this.itemPreview('sa-script');
    },
    onInterfaces: function() {
        this.itemPreview('sa-interface_count');
    },
    onSensors: function() {
        this.itemPreview('sa-sensors');
    },
    onCPE: function() {},
    onLinks: function() {
        this.itemPreview('sa-link_count');
    },
    onDiscovery: function() {
        this.itemPreview('sa-discovery');
    },
    onAlarm: function() {
        this.itemPreview('sa-alarms');
    },
    onMaintenance: function() {},
    onInventory: function() {
        this.itemPreview('sa-inventory');
    },
    onInteractions: function() {
        this.itemPreview('sa-interactions');
    },
    onValidationSettings: function() {},
    onCaps: function() {},
    onHelpOpener: function() {},
    newRecord: function(defaults) {
        var defaultValues = {},
            view = this.getView(),
            formPanel = this.getView().down('[itemId=managedobject-form-panel]'),
            fieldsWithDefaultValue = Ext.Array.filter(Ext.create("NOC.sa.managedobject.Model").fields,
                function(field) {return !Ext.isEmpty(field.defaultValue)});

        Ext.Array.each(fieldsWithDefaultValue, function(field) {
            defaultValues[field.name] = field.defaultValue;
        });
        view.up('[itemId=sa-managedobject]').getController().setFormTitle(__("Create") + " {0}", "NEW");
        formPanel.recordId = undefined;
        formPanel.getForm().reset();
        formPanel.getForm().setValues(defaultValues);
        view.up('[itemId=sa-managedobject]').getController().resetInlineStore(formPanel, defaults);
        view.down('[itemId=cloneBtn]').setDisabled(true);
        view.down('[itemId=createBtn]').setDisabled(true);
        view.down('[itemId=deleteBtn]').setDisabled(true);
    },
    saveRecord: function(data) {
        var me = this,
            formPanel = this.getView().down('[itemId=managedobject-form-panel]'),
            record = Ext.create("NOC.sa.managedobject.Model");

        record.self.setProxy({type: "managedobject"});
        if(!record.validate().isValid()) {
            // @todo: Error report
            NOC.error(__("Invalid data!"));
            return;
        }
        record.set("id", formPanel.recordId);
        if(formPanel.recordId) {
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
                me.reloadSelectionGrids();
                me.toMain();
                NOC.msg.complete(__("Saved"));
            },
            failure: function(record, operation) {
                var message = "Error saving record";
                me.getView().unmask();
                if(operation && operation.error && operation.error.response && operation.error.response.responseText) {
                    var response = Ext.decode(operation.error.response.responseText);
                    if(response && response.message) {
                        message = response.message;
                    }
                }
                NOC.error(message);
            },
        });
    },
    deleteRecord: function() {
        var form = this.getView().down('[itemId=managedobject-form-panel]'),
            record = Ext.create("NOC.sa.managedobject.Model");

        record.self.setProxy({type: "managedobject"});
        if(form.recordId) {
            this.getView().mask(__("Deleting ..."));
            Ext.Ajax.request({
                url: "/sa/managedobject/" + form.recordId + "/",
                method: "DELETE",
                scope: this,
                success: function(response) {
                    // Process result
                    this.reloadSelectionGrids();
                    this.toMain();
                    this.getView().unmask();
                },
                failure: function(response) {
                    var message;
                    try {
                        message = Ext.decode(response.responseText).message;
                    } catch(err) {
                        message = "Internal error";
                    }
                    NOC.error(message);
                    this.unmask();
                }
            });
        }
    },
    reloadSelectionGrids: function() {
        this.getView().up('[itemId=sa-managedobject]').down('[reference=saManagedobjectSelectionGrid]').getStore().reload();
        // ToDo update reference=saManagedobjectSelectedGrid1, take new values from reference=saManagedobjectSelectionGrid
        var basketGrid = this.getView().up('[itemId=sa-managedobject]').down('[reference=saManagedobjectSelectedGrid1]'),
            ids = Ext.Array.map(basketGrid.getStore().getData().items, function(record) {return record.id});
        if(ids.length > 0) {
            basketGrid.mask(__("Loading"));
            Ext.Ajax.request({
                url: this.url + "full/",
                method: "POST",
                scope: this,
                jsonData: {
                    id__in: ids,
                },
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    basketGrid.unmask();
                    basketGrid.getStore().loadData(data);
                },
                failure: function() {
                    basketGrid.unmask();
                    if(gridView) {
                        parentCmp.unmask();
                    }
                    NOC.error(__("Failed refresh basket"));
                }
            });
        }
    },
    gotoItem: function(itemName) {
        var mainView = this.getView().up('[appId=sa.managedobject]');
        mainView.setActiveItem(itemName);
        mainView.setHistoryHash();
    },
    itemPreview: function(itemName) {
        var mainView = this.getView(),
            backItem = mainView.down('[itemId=managedobject-form-panel]'),
            activeItem = mainView.setActiveItem(itemName);
        if(activeItem !== false) {
            activeItem.app = mainView.up('[appId=sa.managedobject]');
            activeItem.preview(backItem.currentRecord, backItem);
        }
    },
    // Workaround labelField
    onChange: Ext.emptyFn,
});