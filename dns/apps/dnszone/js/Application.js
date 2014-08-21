//---------------------------------------------------------------------
// dns.dnszone application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszone.Application");

Ext.define("NOC.dns.dnszone.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.dns.dnszone.Model",
        "NOC.dns.dnszone.RecordsModel",
        "NOC.dns.dnszone.RRTypeField",
        "NOC.dns.dnszoneprofile.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.project.project.LookupField"
    ],
    model: "NOC.dns.dnszone.Model",
    search: true,

    initComponent: function () {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Gen.",
                    dataIndex: "is_auto_generated",
                    renderer: NOC.render.Bool,
                    width: 30
                },
                {
                    text: "Serial",
                    dataIndex: "serial",
                    width: 75
                },
                {
                    text: "Profile",
                    dataIndex: "profile",
                    renderer: NOC.render.Lookup("profile"),
                    width: 100
                },
                {
                    text: "Project",
                    dataIndex: "project",
                    renderer: NOC.render.Lookup("project"),
                    width: 150
                },
                {
                    text: "Paid Till",
                    dataIndex: "paid_till",
                    width: 100,
                    format: "Y-m-d",
                    startDay: 1,
                    renderer: NOC.render.Date
                },
                {
                    text: "Notification",
                    dataIndex: "notification_group",
                    renderer: NOC.render.Lookup("notification_group"),
                    width: 100
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: "Tags",
                    dataIndex: "tags",
                    renderer: NOC.render.Tags
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Domain",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textfield",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "is_auto_generated",
                    xtype: "checkboxfield",
                    boxLabel: "Auto generated?",
                    allowBlank: false
                },
                {
                    name: "serial",
                    xtype: "numberfield",
                    fieldLabel: "Serial",
                    allowBlank: false
                },
                {
                    name: "profile",
                    xtype: "dns.dnszoneprofile.LookupField",
                    fieldLabel: "Profile",
                    allowBlank: false
                },
                {
                    name: "project",
                    xtype: "project.project.LookupField",
                    fieldLabel: "Project",
                    allowBlank: true
                },
                {
                    name: "notification_group",
                    xtype: "main.notificationgroup.LookupField",
                    fieldLabel: "Notification Group",
                    allowBlank: true
                },
                {
                    name: "paid_till",
                    xtype: "datefield",
                    fieldLabel: "Paid Till",
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: "Tags",
                    allowBlank: true
                }
            ],
            inlines: [
                {
                    title: "Records",
                    model: "NOC.dns.dnszone.RecordsModel",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: "TTL",
                            dataIndex: "ttl",
                            width: 50,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "Type",
                            dataIndex: "type",
                            width: 75,
                            editor: {
                                xtype: "dns.dnszone.RRTypeField",
                                listeners: {
                                    scope: me,
                                    select: me.onSelectRRType
                                }
                            }
                        },
                        {
                            text: "Prio.",
                            dataIndex: "priority",
                            width: 50,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "Content",
                            dataIndex: "content",
                            flex: 1,
                            editor: {
                                xtype: "textfield",
                                allowBlank: false
                            }
                        },
                        {
                            text: "Tags",
                            dataIndex: "tags",
                            width: 100,
                            editor: "tagsfield"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: "By Profile",
            name: "profile",
            ftype: "lookup",
            lookup: "dns.dnszoneprofile"
        },
        {
            title: "By Project",
            name: "project",
            ftype: "lookup",
            lookup: "project.project"
        },
        {
            title: "By Notification",
            name: "notification_group",
            ftype: "lookup",
            lookup: "main.notificationgroup"
        },
        {
            title: "By Tags",
            name: "tags",
            ftype: "tag"
        }
    ],
    preview: {
        xtype: "NOC.core.RepoPreview",
        syntax: "bind",
        previewName: "Zone: {{name}}",
        restUrl: "/dns/dnszone/{{id}}/repo/zone/"
    },
    // Check RRType accepts priority field
    isPrioVisible: function(rrType) {
        var me = this;
        return (
            (rrType === "MX") ||
            (rrType === "SRV")
        );
    },

    onSelectRRType: function(combo, records, eOpts) {
        var me = this,
            rrType = combo.getValue(),
            prioCombo = combo.ownerCt.items.items[3];
        prioCombo.setDisabled(!me.isPrioVisible(rrType));
    },

    onInlineBeforeEdit: function(plugin, context, eOpts) {
        var me = this,
            prioCombo = plugin.editor.items.items[3];
        me.callParent(arguments);
        prioCombo.setDisabled(!me.isPrioVisible(context.record.get("type")));
    }
});
