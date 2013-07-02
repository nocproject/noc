//---------------------------------------------------------------------
// pm.check application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.Application");

Ext.define("NOC.pm.check.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.pm.pmcheck.Model",
        "NOC.pm.storage.LookupField",
        "NOC.pm.probe.LookupField",
        "NOC.main.ref.check.LookupField",
    ],
    model: "NOC.pm.check.Model",
    search: true,
    previewIcon: "icon_chart_curve",
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Active",
            dataIndex: "is_active",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Storage",
            dataIndex: "storage",
            renderer: NOC.render.Lookup("storage"),
            width: 150
        },
        {
            text: "Probe",
            dataIndex: "probe",
            renderer: NOC.render.Lookup("probe"),
            width: 150
        },
        {
            text: "Check",
            dataIndex: "check",
            width: 150
        },
        {
            text: "Interval",
            dataIndex: "interval",
            width: 75
        }
    ],

    filters: [
        {
            title: "Is Active",
            name: "is_active",
            ftype: "boolean"
        }
    ],

    initComponent: function() {
        var me = this;
        //
        me.graphPanel = Ext.create("NOC.pm.ts.GraphPreview", {app: me});
        me.ITEM_GRAPH = me.registerItem(me.graphPanel);
        // Passed by get_launch_info
        me.checkForms = me.noc.check_forms;
        me.configPanel = Ext.create("Ext.container.Container", {
            title: "Configuration"
        });
        me.configForm = null;
        me.firstEdit = false;
        Ext.apply(me, {
            fields: [
                {
                    name: "name",
                    fieldLabel: "Name",
                    xtype: "textfield",
                    allowBlank: false
                },
                {
                    name: "is_active",
                    xtype: "checkboxfield",
                    boxLabel: "Active"
                },
                {
                    name: "probe",
                    fieldLabel: "Probe",
                    xtype: "pm.probe.LookupField",
                    allowBlank: false
                },
                {
                    name: "storage",
                    fieldLabel: "Storage",
                    xtype: "pm.storage.LookupField",
                    allowBlank: false
                },
                {
                    name: "check",
                    fieldLabel: "Check",
                    xtype: "main.ref.check.LookupField",
                    allowBlank: false,
                    listeners: {
                        select: {
                            scope: me,
                            fn: me.onCheckSelect
                        }
                    }
                },
                {
                    name: "interval",
                    fieldLabel: "Interval",
                    xtype: "numberfield",
                    allowBlank: false,
                    defaultValue: 60
                },
                {
                    xtype: "container",
                    html: "Configuration:",
                    height: 20,
                    style: {
                        "font-weight": "bold",
                        "text-decoration": "underline"
                    }
                },
                me.configPanel
            ]
        });
        me.callParent();
    },
    //
    onEditRecord: function(record) {
        var me = this;
        me.firstEdit = true;
        me.callParent([record]);
    },
    //
    saveRecord: function(data) {
        var me = this;
        data.config = me.configForm.getValues();
        me.callParent([data]);
    },
    //
    onCheckSelect: function(combo, records, opts) {
        var me = this,
            fclass = me.checkForms[records[0].get("id")],
            oldValues = null;
        if(me.firstEdit) {
            me.firstEdit = false;
            oldValues = me.currentRecord.get("config");
        } else if(me.configForm) {
            oldValues = me.configForm.getValues();
        }
        me.configForm = Ext.create(fclass, {
            defaults: {
                anchor: "100%"
            },
            border: false,
            listeners: {
                beforeadd: function(me, field) {
                    // Change label style for required fields
                    if(field.xtype == "fieldset") {
                        for(var key in field.items.items) {
                            if (!field.items.items[key].allowBlank)
                                field.items.items[key].labelClsExtra = "noc-label-required";
                        }
                    } else {
                        if(!field.allowBlank)
                           field.labelClsExtra = "noc-label-required";
                    }
                }
            }
        });
        me.configPanel.removeAll();
        me.configPanel.add(me.configForm);
        if(oldValues) {
            me.configForm.getForm().setValues(oldValues);
        }
    },
    //
    onPreview: function(record) {
        var me = this;

        Ext.Ajax.request({
            url: "/pm/check/" + record.get("id") + "/ts/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.showItem(me.ITEM_GRAPH);
                me.graphPanel.setTS(data);
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    }
});
