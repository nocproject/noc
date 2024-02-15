//---------------------------------------------------------------------
// NOC.login application, set admin form
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.SetAdminView");

__ = function(x) {return x}

Ext.define('NOC.SetAdminView', {
    extend: 'Ext.window.Window'
    , xtype: 'setAdmin'
    , autoShow: true
    , closable: false
    , resizable: false
    , title: __("Setting Admin")
    , layout: 'fit'
    , modal: true
    , defaultListenerScope: true
    , defaultFocus: 'user'
    , defaultButton: 'okButton'
    , referenceHolder: true
    , requires: [
        'Ext.form.Panel',
        'Ext.window.Toast'
    ]
    , viewModel: 'default'
    , items: {
        xtype: 'form'
        , padding: 15
        , reference: 'setAdminForm'
        , fixed: true
        , border: false
        , bodyStyle: {
            background: '#e0e0e0',
            padding: '10px'
        }
        , autoEl: {
            tag: 'form'
        }
        , defaults: {
            anchor: '100%'
            , allowBlank: false
            , enableKeyEvents: true
            , xtype: 'textfield'
        }
        , items: [{
            xtype: 'displayfield'
            , value: __('Type admin name and password:')
            , hideLabel: true
        }, {
            xtype: 'textfield'
            , itemId: 'user'
            , name: 'user'
            , bind: '{user}'
            , fieldLabel: __('Admin')
            , blankText: __('User name cannot be empty')
            // , listeners: {
            //     afterrender: 'afterRender'
            // }
        }, {
            xtype: 'textfield'
            , itemId: 'password'
            , name: 'password'
            , bind: '{password}'
            , fieldLabel: __('Password')
            , blankText: __('Password cannot be empty')
            , inputType: 'password'
            // , listeners: {
            //     afterrender: 'afterRender'
            // }
        }],
        buttons: [{
            reference: 'okButton'
            , formBind: true
            , handler: 'onSetClick'
            , text: __('Set')
            , autoEl: {
                // tag: 'input',
                // type: 'submit'
            }
            , listeners: {
                beforerender: function() {
                    if(!Ext.isIE) {
                        Ext.apply(this.autoEl, {type: 'submit'})
                    }
                }
            }
        }]
    }
    , initComponent: function() {
        var param = Ext.urlDecode(location.search);
        if('msg' in param) {
            this.items.items[0].value = param.msg + '<br/>' + this.items.items[0].value
        }
        this.callParent();
    }
    , onSetClick: function() {
        var data = this.getViewModel().getData(),
            params = Ext.encode({
                user_name: data.user,
                password: data.password
            });
        if(params !== undefined) {
            Ext.Ajax.request({
                // url: 'http://localhost:3000/api/login/set_admin/'
                url: '/api/login/set_admin/'
                , params: params
                , method: 'POST'
                , success: Ext.Function.pass(this.onSuccess, this.onFailure)
                , failure: this.onFailure
                , defaultPostHeader: 'application/json'
            });
        }
    }
    , onSuccess: function() {
        document.location = '/' + location.hash;
    }
    , onFailure: function() {
        Ext.toast({
            html: '<div style="text-align: center;">' + __('Failed to set admin user') + '</div>',
            align: 't',
            paddingY: 0,
            width: '80%',
            minHeight: 5,
            border: false,
            listeners: {
                focusenter: function() {
                    this.close();
                }
            },
            bodyStyle: {
                color: 'white',
                background: 'red',
                "font-weight": 'bold'
            },
            style: {
                background: 'red',
                "border-width": '0px'
            }
        });
    }
});