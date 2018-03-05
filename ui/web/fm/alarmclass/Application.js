//---------------------------------------------------------------------
// fm.alarmclass application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.fm.alarmclass.Application');

Ext.define('NOC.fm.alarmclass.Application', {
    extend: 'NOC.core.ModelApplication',
    requires: [
        'NOC.fm.alarmclass.Model',
        'NOC.fm.alarmclass.LookupField',
        'NOC.fm.alarmseverity.LookupField',
        'Ext.ux.form.JSONField',
        'Ext.ux.form.StringsField'
    ],
    model: 'NOC.fm.alarmclass.Model',
    search: true,
    treeFilter: 'category',
    rowClassField: 'row_class',

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create('NOC.core.JSONPreview', {
            app: me,
            restUrl: new Ext.XTemplate('/fm/alarmclass/{id}/json/'),
            previewName: new Ext.XTemplate('Alarm Class: {name}')
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __('Name'),
                    dataIndex: 'name',
                    width: 250
                },
                {
                    text: __('Builtin'),
                    dataIndex: 'is_builtin',
                    renderer: NOC.render.Bool,
                    width: 30
                },
                {
                    text: __('Description'),
                    dataIndex: 'description',
                    flex: 1
                }
            ],
            fields: [
                {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [
                        {
                            name: 'name',
                            xtype: 'textfield',
                            fieldLabel: __('Name'),
                            allowBlank: false,
                            uiStyle: 'large'
                        },
                        {
                            name: 'uuid',
                            xtype: 'displayfield',
                            style: 'padding-left: 10px',
                            fieldLabel: __('UUID')
                        }
                    ]
                },
                {
                    xtype: 'tabpanel',
                    layout: 'fit',
                    autoScroll: true,
                    anchor: '-0, -50',
                    defaults: {
                        autoScroll: true,
                        layout: 'anchor'
                    },
                    items: [ // tabs
                        {
                            title: __('Text'),
                            items: [
                                {
                                    name: 'description',
                                    xtype: 'textarea',
                                    fieldLabel: __('Description'),
                                    uiStyle: 'extra'
                                },
                                {
                                    name: 'subject_template',
                                    xtype: 'textfield',
                                    fieldLabel: __('Subject Template'),
                                    uiStyle: 'extra',
                                    allowBlank: false
                                },
                                {
                                    name: 'body_template',
                                    xtype: 'textarea',
                                    fieldLabel: __('Body Template'),
                                    uiStyle: 'extra',
                                    allowBlank: false
                                },
                                {
                                    name: 'symptoms',
                                    xtype: 'textarea',
                                    fieldLabel: __('Symptoms'),
                                    uiStyle: 'extra',
                                    allowBlank: true
                                },
                                {
                                    name: 'probable_causes',
                                    xtype: 'textarea',
                                    fieldLabel: __('Probable Causes'),
                                    uiStyle: 'extra',
                                    allowBlank: true
                                },
                                {
                                    name: 'recommended_actions',
                                    xtype: 'textarea',
                                    fieldLabel: __('Recommended Actions'),
                                    uiStyle: 'extra',
                                    allowBlank: true
                                }
                            ]
                        }, // Text
                        {
                            title: __('Severity'),
                            items: [
                                {
                                    name: 'default_severity',
                                    xtype: 'fm.alarmseverity.LookupField',
                                    fieldLabel: __('Default Severity')
                                },
                                {
                                    name: 'is_unique',
                                    xtype: 'checkboxfield',
                                    boxLabel: __('Unique')
                                },
                                {
                                    name: 'user_clearable',
                                    xtype: 'checkboxfield',
                                    boxLabel: __('User Clearable')
                                },
                                {
                                    name: 'discriminator',
                                    xtype: 'stringsfield',
                                    fieldLabel: __('Discriminator')
                                }
                            ]
                        }, // Severity
                        {
                            title: __('Variables'),
                            items: [
                                {
                                    name: 'vars',
                                    xtype: 'gridfield',
                                    columns: [
                                        {
                                            text: __('Name'),
                                            dataIndex: 'name',
                                            width: 100,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Description'),
                                            dataIndex: 'description',
                                            flex: 1,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Default'),
                                            dataIndex: 'default',
                                            width: 150,
                                            editor: 'textfield'
                                        }
                                    ]
                                }
                            ]
                        }, // Variables
                        {
                            title: __('Data Sources'),
                            items: [
                                {
                                    name: 'datasources',
                                    xtype: 'gridfield',
                                    columns: [
                                        {
                                            text: __('Name'),
                                            dataIndex: 'name',
                                            width: 100,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Datasource'),
                                            dataIndex: 'datasource',
                                            width: 100,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Search'),
                                            dataIndex: 'search',
                                            flex: 1,
                                            editor: 'jsonfield',
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        }, // Data Sources
                        {
                            title: __('Root Cause'),
                            items: [
                                {
                                    name: 'root_cause',
                                    xtype: 'gridfield',
                                    columns: [
                                        {
                                            text: __('Name'),
                                            dataIndex: 'name',
                                            width: 200,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Root'),
                                            dataIndex: 'root',
                                            renderer: NOC.render.Lookup('root'),
                                            editor: 'fm.alarmclass.LookupField',
                                            width: 200
                                        },
                                        {
                                            text: __('Window'),
                                            dataIndex: 'window',
                                            width: 50,
                                            editor: 'numberfield'
                                        },
                                        {
                                            text: __('Condition'),
                                            dataIndex: 'condition',
                                            editor: 'textfield',
                                            width: 150
                                        },
                                        {
                                            text: __('Match Condition'),
                                            dataIndex: 'match_condition',
                                            editor: 'jsonfield',
                                            flex: 1,
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        }, // Root Cause
                        {
                            title: __('Jobs'),
                            items: [
                                {
                                    name: 'jobs',
                                    xtype: 'gridfield',
                                    columns: [
                                        {
                                            text: __('Job'),
                                            dataIndex: 'job',
                                            width: 100,
                                            editor: 'textfield'
                                        },
                                        {
                                            text: __('Interval'),
                                            dataIndex: 'interval',
                                            width: 50,
                                            editor: 'numberfield'
                                        },
                                        {
                                            text: __('Vars'),
                                            dataIndex: 'vars',
                                            flex: 1,
                                            editor: 'jsonfield',
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        }, // Jobs
                        {
                            title: __('Handlers'),
                            items: [
                                {
                                    xtype: 'stringsfield',
                                    name: 'handlers',
                                    fieldLabel: __('Handlers')
                                },
                                {
                                    xtype: 'stringsfield',
                                    name: 'clear_handlers',
                                    fieldLabel: __('Clear Handlers')
                                }
                            ]
                        }, // Handlers
                        {
                            title: __('Plugins'),
                            items: [
                                {
                                    xtype: 'gridfield',
                                    name: 'plugins',
                                    fieldLabel: __('Plugins'),
                                    columns: [
                                        {
                                            text: __('Name'),
                                            dataIndex: 'name',
                                            editor: 'textfield',
                                            width: 150
                                        },
                                        {
                                            text: __('Config'),
                                            dataIndex: 'config',
                                            editor: 'jsonfield',
                                            flex: 1,
                                            renderer: NOC.render.JSON
                                        }
                                    ]
                                }
                            ]
                        }, // Plugins
                        {
                            title: __('Timing'),
                            defaults: {
                                labelWidth: 150
                            },
                            items: [
                                {
                                    name: 'flap_condition',
                                    xtype: 'combobox',
                                    fieldLabel: __('Flap Condition'),
                                    tooltip: __('Flap detection'),
                                    allowBlank: false,
                                    uiStyle: 'small',
                                    store: [
                                        ['none', __('None')],
                                        ['count', __('Count')]
                                    ],
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'flap_window',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Flap Window (sec)'),
                                    tooltip: __('Time in seconds, while waiting of reopen'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'flap_threshold',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Flap Threshold (pcs)'),
                                    tooltip: __('Number of flaps while close Flap Window'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'notification_delay',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Notification Delay (sec)'),
                                    tooltip: __('Time in seconds to delay alarm risen notification'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'control_time0',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Control Time 0 (sec)'),
                                    tooltip: __('Control time to reopen alarm instead of creating new'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'control_time1',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Control Time 1 (sec)'),
                                    tooltip: __('Control time to reopen alarm after 1 reopen'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'control_timeN',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Control Time N (sec)'),
                                    tooltip: __('Control time to reopen alarm after >1 reopen'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: 'recover_time',
                                    xtype: 'numberfield',
                                    fieldLabel: __('Recover Time (sec)'),
                                    tooltip: __('Consequence recover time. Root cause will be detached if consequence alarm will not clear itself in *recover_time*'),
                                    allowBlank: true,
                                    uiStyle: 'small',
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ]
                        }  // Timing
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __('JSON'),
                    glyph: NOC.glyph.file,
                    tooltip: __('View as JSON'),
                    hasAccess: NOC.hasPermission('read'),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    filters: [
        {
            title: __('By Builtin'),
            name: 'is_builtin',
            ftype: 'boolean'
        }
    ],
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    },
    //
    addTooltip: function(element) {
        Ext.create('Ext.tip.ToolTip', {
            target: element.getEl(),
            html: element.tooltip
        });
    }
});
