//---------------------------------------------------------------------
// report control widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ReportControl");

Ext.define("NOC.core.ReportControl", {
    extend: "Ext.panel.Panel",
    alias: "widget.report.control",

    initComponent: function() {
        var me = this;

        me.columnsStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label", {
                name: "is_active",
                type: "boolean"
            }],
            data: me.storeData
        });

        me.columnsGrid = Ext.create("Ext.grid.Panel", {
            store: me.columnsStore,
            scrollable: true,
            maxHeight: 300,
            columns: [
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Field"),
                    dataIndex: "label",
                    flex: 1
                }
            ],
            selModel: "cellmodel",
            plugins: [
                {
                    ptype: "cellediting",
                    clicksToEdit: 1
                }
            ],
            viewConfig: {
                plugins: {
                    ptype: "gridviewdragdrop",
                    dragText: __("Drag and drop to reorganize")
                }
            }
        });

        me.formatButton = Ext.create("Ext.button.Segmented", {
            width: 150,
            items: [
                {
                    text: __("CSV"),
                    value: "csv",
                    width: 70
                },
                {
                    text: __("Excel"),
                    value: "xlsx",
                    pressed: true,
                    width: 70
                }
            ]
        });

        me.formPanel = Ext.create("Ext.form.Panel", {
            autoScroll: true,
            defaults: {
                labelWidth: 120,
                padding: "5 10 5 10"
            },
            items: me.controls.concat([
                me.formatButton,
                me.columnsGrid
            ]),
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Download"),
                            glyph: NOC.glyph.download,
                            scope: me,
                            handler: me.onDownload,
                            formBind: true
                        }
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [me.formPanel]
        });
        me.callParent();
    },
    //
    onDownload: function() {
        var me = this,
            url = [
                me.url + "/download/?o_format=" + me.formatButton.getValue()
            ],
            columns = [],
            setParam = function(control) {
                if(control.hasOwnProperty("name")) {
                    var field = this.down("[name=" + control.name + "]"), val;
                    if(Ext.isFunction(field.getSubmitValue)) { // datefield
                        val = field.getSubmitValue();
                    } else {
                        val = field.getValue();
                        if(Ext.isObject(val) && val.hasOwnProperty(control.name)) { // radiobutton
                            val = val[control.name];
                        }
                    }
                    if(val) {
                        url.push("&" + control.name + "=" + val);
                    }
                }
            },
            setColumn = function(record) {
                if(record.get("is_active")) {
                    columns.push(record.get("id"));
                }
            };

        Ext.each(me.controls, setParam, me);
        me.columnsStore.each(setColumn);
        url.push("&columns=" + columns.join(","));
        window.open(url.join(""));
    }
});
