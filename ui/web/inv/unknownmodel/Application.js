//---------------------------------------------------------------------
// inv.unknownmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.unknownmodel.Application");

Ext.define("NOC.inv.unknownmodel.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.unknownmodel.Model",
        "NOC.inv.objectmodel.LookupField"
    ],
    model: "NOC.inv.unknownmodel.Model",
    search: true,
    actions: [
        {
            title: __("Remove"),
            action: "remove",
            glyph: NOC.glyph.remove
        }
    ],
    initComponent: function() {
        var me = this;

        me.ITEM_MAGIC = me.registerItem("NOC.inv.unknownmodel.MagicPanel");

        Ext.apply(me, {
            columns: [
                {
                    text: __("Object"),
                    dataIndex: "managed_object",
                    width: 100
                },
                {
                    text: __("Platform"),
                    dataIndex: "platform",
                    width: 100
                },
                {
                    text: __("Vendor"),
                    dataIndex: "vendor",
                    width: 70
                },
                {
                    text: __("Part No"),
                    dataIndex: "part_no",
                    width: 100
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            formToolbar: [],
            fields: [
                {
                    name: "managed_object",
                    xtype: "displayfield",
                    fieldLabel: __("Object"),
                    labelWidth: 150,
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    xtype: "inv.objectmodel.LookupField",
                    name: "type",
                    fieldLabel: __("Use connections from"),
                    labelWidth: 150,
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    xtype: "button",
                    text: __("Generate"),
                    glyph: NOC.glyph.magic,
                    maxWidth: 80,
                    scope: me,
                    handler: function() {
                        var me = this,
                            formData = this.form.getValues();
                        new Ext.Promise(function(resolve) {
                            Ext.Ajax.request({
                                url: "/inv/vendor/lookup/?__format=ext&__limit=2&__query=" + me.currentRecord.get("vendor"),
                                method: 'GET',
                                scope: me,
                                success: function(response) {
                                    var result = Ext.decode(response.responseText);
                                    if(result.hasOwnProperty("total") && result.total === 1) {
                                        resolve(result.data[0]);
                                    } else if(result.hasOwnProperty("total") && result.total === 0) {
                                        NOC.error(__("Vendor not found!"));
                                    } else {
                                        NOC.error(__("Too many vendors found!"));
                                    }
                                },
                                failure: function() {
                                    NOC.error(__('Failed to get vendor information'));
                                }
                            })
                        }).then(function(vendor) {
                            Ext.Ajax.request({
                                url: "/inv/objectmodel/" +formData.type + "/",
                                method: 'GET',
                                scope: me,
                                success: function(response) {
                                    var result = Ext.decode(response.responseText);
                                    if(result.hasOwnProperty("connections")) {
                                        NOC.run(
                                            "NOC.inv.objectmodel.Application",
                                            __("Create Model"),
                                            {
                                                cmd: {
                                                    cmd: "new",
                                                    args: {
                                                        description: Ext.String.format("{0} generated from {1}, platform: {2}",
                                                            me.currentRecord.get("description"),
                                                            me.currentRecord.get("managed_object"),
                                                            me.currentRecord.get("platform")),
                                                        data: {
                                                            asset: {
                                                                part_no: [me.currentRecord.get("part_no")]
                                                            }
                                                        },
                                                        connections: result.connections,
                                                        vendor: vendor.id,
                                                        vendor__label: vendor.label

                                                        // connection_rule: "5717afb6cc044b7708f51558",
                                                        // connection_rule__label: "Cisco | 7200",
                                                        // cr_context: "CHASSIS",
                                                        // data: {
                                                        //     "management": {"managed": true},
                                                        //     "asset": {"part_no": ["CISCOUBR7246VXR"]},
                                                        //     "rackmount": {"units": 7}
                                                        // },
                                                        // connections: [
                                                        //     {
                                                        //         "name": "sup",
                                                        //         "type": "5717afb7cc044b7708f5165b",
                                                        //         "group": null,
                                                        //         "direction": "i",
                                                        //         "gender": "f",
                                                        //         "cross": null,
                                                        //         "protocols": [],
                                                        //         "internal_name": null,
                                                        //         "description": "Supervisor slot"
                                                        //     }, {
                                                        //         "name": "linecard1",
                                                        //         "type": "5717afb7cc044b7708f51667",
                                                        //         "group": null,
                                                        //         "direction": "i",
                                                        //         "gender": "f",
                                                        //         "cross": null,
                                                        //         "protocols": [],
                                                        //         "internal_name": null,
                                                        //         "description": "Linecard 1 slot"
                                                        //     }, {
                                                        //         "name": "linecard2",
                                                        //         "type": "5717afb7cc044b7708f51667",
                                                        //         "group": null,
                                                        //         "direction": "i",
                                                        //         "gender": "f",
                                                        //         "cross": null,
                                                        //         "protocols": [],
                                                        //         "internal_name": null,
                                                        //         "description": "Linecard 2 slot"
                                                        //     }, {
                                                        //         "name": "pwr0",
                                                        //         "type": "5717afb6cc044b7708f51608",
                                                        //         "group": null,
                                                        //         "direction": "i",
                                                        //         "gender": "f",
                                                        //         "cross": null,
                                                        //         "protocols": [],
                                                        //         "internal_name": null,
                                                        //         "description": "PSU0"
                                                        //     }, {
                                                        //         "name": "pwr1",
                                                        //         "type": "5717afb6cc044b7708f51608",
                                                        //         "group": null,
                                                        //         "direction": "i",
                                                        //         "gender": "f",
                                                        //         "cross": null,
                                                        //         "protocols": [],
                                                        //         "internal_name": null,
                                                        //         "description": "PSU1"
                                                        //     }],
                                                        // id: "NOC.inv.objectmodel.Model-sm-1",
                                                        // is_builtin: false,
                                                        // fav_status: false
                                                    }
                                                }
                                            }
                                        );
                                    } else {
                                        NOC.error(__("No connection information"));
                                    }
                                },
                                failure: function() {
                                    NOC.error(__("Failed to get connection information"));
                                }
                            })
                        });
                    }
                }
            ]
        });
        me.callParent();
    }
});
