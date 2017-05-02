//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.getnow.Application");
Ext.define("NOC.sa.getnow.Application", {
    extend: "NOC.core.Application",
    requires: [
        'NOC.sa.getnow.AppController',
        'NOC.sa.getnow.ViewModel',
        'NOC.core.Filter',
        'NOC.sa.getnow.SelectionGrid'
    ],

    layout: 'border',
    controller: 'getnow',
    viewModel: 'getnow',
    border: false,
    stateful: true,
    stateId: 'getnow.appPanel',

    initComponent: function() {
        Ext.apply(this, {
            items: [
                {
                    xtype: 'selectionGrid',
                    region: 'west',
                    resizable: true,
                    split: true,
                    width: '35%'
                },
                {
                    xclass: 'NOC.core.RepoPreview',
                    region: 'center',
                    width: '65%',
                    app: this,
                    reference: 'repoPreview',
                    previewName: '{0} config',
                    restUrl: '/sa/managedobject/{0}/repo/cfg/',
                    historyHashPrefix: 'config',
                    tbar: [
                        {
                            text: __('Get config NOW'),
                            tooltip: __('Get config NOW'),
                            bind: {
                                disabled: '{!selectionGrid.selection}'
                            },
                            handler: 'onGetConfig'
                        },
                        {
                            text: __('Stop Polling'),
                            tooltip: __('Stop Polling'),
                            bind: {
                                disabled: '{!isStarted}'
                            },
                            handler: 'onStopPolling'
                        },
                        '->',
                        {
                            xtype: 'box',
                            bind: {
                                html: '<span style="text-align: center;" class="noc-badge {polling.style}">{polling.leave}</span>'
                            }
                        }
                    ]
                },
                {
                    xtype: 'NOC.Filter',
                    appId: this.appId,
                    reference: 'filterPanel',
                    stateful: true,
                    stateId: 'getnow.filterPanel',
                    selectionStore: this.getViewModel().getStore('objectsStore')
                }
            ]
        });
        this.callParent();
    }
});