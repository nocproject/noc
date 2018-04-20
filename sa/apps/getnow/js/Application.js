/**
 * Created by boris on 01.09.14.
 */
console.debug("Defining NOC.sa.getnow.Application");
Ext.define("NOC.sa.getnow.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.sa.managedobject.SchemeLookupField",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.core.QuickRepoPreview"
    ],
    pollingInterval: 3000,
    layout: "card",
    rowClassField: "row_class",
    historyHashPrefix: null,
    restUrl: "/sa/managedobject/{{id}}/repo/cfg/",
    theme: "default",
    syntax: "groovy",
    taskStates: {},
    stylesInfo: {},
    stateCodeToName: {
        W: "Wait",
        R: "Run",
        S: "Stop",
        F: "Fail",
        D: "Disabled",
        true: "OK",
        false: "Fail"
    },
    initComponent: function () {
        var me = this,
            bs = Math.ceil(screen.height / 24);
        me.pollingTaskHandler = Ext.bind(me.pollingTask, me);
        me.store = Ext.create("NOC.core.ModelStore", {
            model: "NOC.sa.getnow.Model",
            autoLoad: true,
            customFields: [],
            filterParams: {},
            pageSize: bs,
            leadingBufferZone: bs,
            numFromEdge: Math.ceil(bs / 2),
            trailingBufferZone: bs
        });

        me.rawButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.android,
            text: "Raw",
            tooltip: "Raw",
            scope: me,
            handler: me.onRaw
        });

        me.managedObject = Ext.create("NOC.sa.managedobject.LookupField", {
            name: "id",
            fieldLabel: "Managed object",
            allowBlank: true,
            valueField: "id",
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.saProfile = Ext.create("NOC.main.ref.profile.LookupField", {
            name: "profile_name",
            fieldLabel: "By SA Profile",
            allowBlank: true,
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.administrativeDomain = Ext.create("NOC.sa.administrativedomain.LookupField", {
            name: "administrative_domain",
            fieldLabel: "By Adm. domain",
            allowBlank: true,
            listeners: {
                scope: me,
                select: me.onChangeFilter
            }
        });

        me.resetFilter = Ext.create("Ext.Button", {
            text: "Reset filter",
            listeners: {
                scope: me,
                click: function () {
                    me.currentQuery = {};
                    me.managedObject.reset();
                    me.saProfile.reset();
                    me.administrativeDomain.reset();
                    me.reloadStore();
                }
            }
        });

        me.selModel = Ext.create("Ext.selection.CheckboxModel", {
            listeners: {
                scope: me,
                selectionchange: me.onActionSelectionChange
            }
        });

        me.getConfigNow = Ext.create("Ext.Button", {
            text: "Get config NOW",
            listeners: {
                scope: me,
                click: function () {
                    me.onGetConfig()
                }
            }
        });

        me.cmContainer = Ext.create({
            xtype: "container",
            layout: "fit",
            tpl: [
                '<div id="{cmpId}-cmEl" class="{cmpCls}" style="{size}"></div>'
            ],
            data: {
                cmpId: me.id,
                cmpCls: Ext.baseCSSPrefix
                    + "codemirror "
                    + Ext.baseCSSPrefix
                    + "html-editor-wrap "
                    + Ext.baseCSSPrefix
                    + "html-editor-input",
                size: "width:100%;height:100%"
            }
        });

        me.currentDeviceLabel = Ext.create("Ext.form.Label", {
            layout: {type: 'hbox', align: 'middle'}
        });

        me.quickRepoPreview = Ext.create("NOC.core.QuickRepoPreview", {
            app: me,
            previewName: "{{name}} config",
            restUrl: "/sa/managedobject/{{id}}/repo/cfg/",
            historyHashPrefix: "config"
        });

        me.gridpanel = Ext.create("Ext.grid.Panel", {
            region: "west",
            split: true,
            store: me.store,
            width: 530,
            selModel: me.selModel,
            listeners: {
                'rowdblclick': function (grid, index, rec) {
                    me.currentDeviceId = index.get("id");
                    me.currentDeviceLabel.setText(index.get("name"));
                    me.quickRepoPreview.preview({"data": index});
                }
            },
            columns: [
                {
                    xtype: 'gridcolumn',
                    text: "ID",
                    dataIndex: "id",
                    width: 30
                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'name',
                    text: 'Managed object',
                    width: 60
                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: "profile_name",
                    text: 'SA Profile'
                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'last_success',
                    text: 'Last success'
                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: "last_update",
                    text: 'Last update'
                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'status',
                    text: 'Status',
                    width: 50,
                    renderer: NOC.render.Choices(me.stateCodeToName)

                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'last_status',
                    text: 'Last status',
                    width: 50,
                    renderer: NOC.render.Choices(me.stateCodeToName)
                }
            ],
            viewConfig: {
                getRowClass: function (record, index, params, store) {
                    var device_id = record.get("id");
                    var status = record.get("status");
                    var last_status = record.get("last_status");
                    if (me.taskStates.hasOwnProperty(device_id)) {
                        var previous_status = me.taskStates[device_id];
                        if (status == "R" && last_status == "S"
                                || previous_status == "I") {
                            me.taskStates[device_id] = "R";
                            return me.stylesInfo["get_now_task_done_in_progress"] || "noc-color-1";
                        }
                        if (status == "W" && last_status == "S") {
                            me.taskStates[device_id] = "S";
                            return me.stylesInfo["get_now_task_done_ok"] || "noc-color-5";
                        }
                        if (status == "W" && last_status == "F") {
                            me.taskStates[device_id] = "F";
                            return me.stylesInfo["get_now_task_done_fail"] || "noc-color-3";
                        }
                    }
                }
            }
        });

        Ext.apply(me, {
            items: [
                {
                    xtype: 'panel',
                    resizable: false,
                    layout: 'border',
                    collapsed: false,
                    manageHeight: false,
                    dockedItems: [
                        {
                            xtype: 'toolbar',
                            dock: 'top',
                            items: [
                                me.managedObject,
                                me.saProfile,
                                me.administrativeDomain,
                                me.resetFilter,
                                "-",
                                me.getConfigNow,
                                "-",
                                me.rawButton
                            ]
                        }
                    ],
                    items: [
                        me.gridpanel,
                        me.quickRepoPreview
                    ]
                }
            ]
        });
        me.callParent();
        me.getStylesInfo();
        me.urlTemplate = Handlebars.compile(me.restUrl);
    },
    onCloseApp: function() {
        var me = this;
        console.log("onCloseApp");
        me.taskStates = {};
    },
    onRaw: function () {
        var me = this;
        var data = me.quickRepoPreview.viewer.getValue();
        var myWindow = window.open();
        myWindow.document.write('<pre>' + data + '</pre>');
    },

    getStylesInfo: function () {
        var me = this;
        Ext.Ajax.request({
            url: "/main/style/",
            method: "GET",
            scope: me,
            failure: function () {
                NOC.error("Failed to run tasks");
            },
            success: function(response) {
                var data = Ext.decode(response.responseText);
                for (var item in data) {
                    var style = data[item];
                    me.stylesInfo[style["name"]] = style["row_class"];
                }
            }
        });
    },

    onActionSelectionChange: function (o, selected, opts) {
        var me = this;
        me.getConfigNow.setDisabled(!selected.length);
    },

    reloadStore: function () {
        var me = this;
        if (me.currentQuery)
            me.store.setFilterParams(me.currentQuery);
        me.store.load();
    },

    onChangeFilter: function () {
        var me = this,
            q = {},
            setIf = function (k, v) {
                if (v) {
                    q[k] = v;
                }
            };
        setIf("managed_object", me.managedObject.getValue());
        setIf("profile_name", me.saProfile.getValue());
        setIf("administrative_domain", me.administrativeDomain.getValue());
        me.currentQuery = q;
        me.reloadStore();
    },

    afterRender: function () {
        var me = this;
        me.callParent(arguments);
    },

    onResize: function () {
        var me = this;
        if (me.viewer) {
            me.viewer.refresh();
        }
    },

    onGetConfig: function () {
        var me = this;
        var selected_devices = me.gridpanel.getSelectionModel().getSelection();
        Ext.each(selected_devices, function (device) {
            var device_id = device.get("id");
            me.runTask(device_id);
            me.taskStates[device_id] = "I";
        });
        me.startPolling();
    },

    runTask: function (id) {
        var me = this;
        Ext.Ajax.request({
            url: "/sa/managedobject/" + id + "/discovery/run/",
            method: "POST",
            scope: me,
            jsonData: {
                "names": ['config_discovery']
            },
            failure: function () {
                NOC.error("Failed to run tasks");
            }
        });
    },

    getStatuses: function () {
        var me = this;
        var in_progress = false;
        for (var device_id in me.taskStates) {
            var status = me.taskStates[device_id];
            if (status == "R" || status == "I")
                in_progress = true;
        }
        if (in_progress) {
            me.reloadStore();
        }
    },

    pollingTask: function () {
        var me = this;
        me.getStatuses();
    },

    startPolling: function () {
        var me = this;
        if (!me.pollingTaskId) {
            me.pollingTaskId = Ext.TaskManager.start({
                run: me.pollingTaskHandler,
                interval: me.pollingInterval
            });
        }
    }
});