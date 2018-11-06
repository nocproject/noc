//---------------------------------------------------------------------
// NOC.core.RepoPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.core.RepoPreview');

Ext.define('NOC.core.RepoPreview', {
    extend: 'NOC.core.ApplicationPanel',
    requires: [
        'NOC.core.RevisionSlider'
    ],
    msg: '',
    layout: 'fit',
    syntax: null,
    restUrl: null,
    scrollable: false,
    historyHashPrefix: null,
    // preview_theme: NOC.settings.preview_theme,
    preview_theme: 'monokai',
    mode: 'groovy',
    viewModel: {
        data: {
            currentSelection: null,
            diffSelection: null
        },
        formulas: {
            canPrevChange: {
                bind: {
                    bindTo: "{currentSelection.selection}"
                },
                get: function(t) {
                    return t && t.store.indexOf(t.data) < t.store.data.length - 1
                }
            },
            canNextChange: {
                bind: {
                    bindTo: "{currentSelection.selection}"
                },
                get: function(t) {
                    return t && t.store.indexOf(t.data) > 0
                }
            },
            canSideBySide: {
                bind: {
                    bindTo: "{diffSelection.selection}"
                },
                get: function(t) {
                    return !!t
                }
            },
            canSwap: {
                bind: {
                    bindTo: "{diffSelection.selection}"
                },
                get: function(t) {
                    return !!t
                }
            }
        }
    },

    initComponent: function() {
        var me = this;

        me.sideBySideModeButton = Ext.create('Ext.button.Button', {
            text: __('Side-By-Side'),
            tooltip: __('Switch on/off side-by-side mode'),
            glyph: NOC.glyph.columns,
            enableToggle: true,
            pressed: false,
            scope: me,
            handler: me.onSideBySide,
            bind: {
                disabled: "{!canSideBySide}"
            }
        });

        me.downloadButton = Ext.create('Ext.button.Button', {
            text: __('Download'),
            tooltip: __('Download config'),
            glyph: NOC.glyph.download,
            scope: me,
            handler: me.onDownload
        });

        me.revCombo = Ext.create('Ext.form.ComboBox', {
            fieldLabel: __('Version'),
            labelWidth: 45,
            labelAlign: 'right',
            width: 210,
            queryMode: 'local',
            displayField: 'ts_label',
            valueField: 'id',
            store: Ext.create('Ext.data.Store', {
                fields: [
                    {
                        name: 'id',
                        type: 'auto'
                    },
                    {
                        name: 'ts',
                        type: 'date'
                    },
                    {
                        name: 'ts_label',
                        mapping: 'ts',
                        convert: function(v, record) {
                            return NOC.render.DateTime(record.get('ts'));
                        }
                    }
                ],
                data: []
            }),
            listeners: {
                scope: me,
                select: me.onSelectRev,
                specialkey: me.onRevSpecialKey
            },
            reference: "currentSelection"
        });

        me.diffCombo = Ext.create('Ext.form.ComboBox', {
            fieldLabel: __('Compare'),
            labelWidth: 45,
            labelAlign: 'right',
            width: 210,
            queryMode: 'local',
            displayField: 'ts_label',
            valueField: 'id',
            store: Ext.create('Ext.data.Store', {
                fields: [
                    {
                        name: 'id',
                        type: 'auto'
                    },
                    {
                        name: 'ts',
                        type: 'date'
                    },
                    {
                        name: 'ts_label',
                        mapping: 'ts',
                        convert: function(v, record) {
                            return NOC.render.DateTime(record.get('ts'));
                        }
                    }
                ],
                data: []
            }),
            listeners: {
                scope: me,
                select: me.onSelectDiff,
                specialkey: me.onDiffSpecialKey
            },
            reference: "diffSelection"
        });

        me.resetButton = Ext.create('Ext.button.Button', {
            glyph: NOC.glyph.refresh,
            text: __('Reset'),
            tooltip: __('Reset'),
            scope: me,
            handler: me.onReset
        });

        me.nextDiffButton = Ext.create('Ext.button.Button', {
            glyph: NOC.glyph.arrow_up,
            tooltip: __('Next change'),
            scope: me,
            handler: me.onNextDiff,
            bind: {
                disabled: "{!canNextChange}"
            }
        });
        //
        me.prevDiffButton = Ext.create('Ext.button.Button', {
            glyph: NOC.glyph.arrow_down,
            tooltip: __('Previous change'),
            scope: me,
            handler: me.onPrevDiff,
            bind: {
                disabled: "{!canPrevChange}"
            }
        });
        //
        me.swapRevButton = Ext.create('Ext.button.Button', {
            glyph: NOC.glyph.exchange,
            tooltip: __('Swap revisions'),
            scope: me,
            handler: me.onSwapRev,
            bind: {
                disabled: "{!canSwap}"
            }
        });

        me.cmContainer = this.getCmContainer();

        CodeMirror.modeURL = '/ui/pkg/codemirror/mode/%N/%N.js';

        Ext.apply(me, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [
                    {
                        itemId: 'close',
                        text: __('Close'),
                        glyph: NOC.glyph.arrow_left,
                        scope: me,
                        handler: me.onBack
                    },
                    me.resetButton,
                    '-',
                    me.revCombo,
                    '-',
                    me.swapRevButton,
                    '-',
                    me.diffCombo,
                    '-',
                    me.prevDiffButton,
                    me.nextDiffButton,
                    me.sideBySideModeButton,
                    me.downloadButton
                ]
            }],
            items: [me.cmContainer],
            listeners: {
                scope: me,
                resize: me.onResize,
                afterrender: me.onAfterRender
            }
        });
        me.callParent();
    },
    //
    onAfterRender: function() {
        var me = this;
        // me.callParent(arguments);
        me.initViewer();
        me.onResize();
    },
    onResize: function() {
        var me = this;
        if(me.viewer && Ext.isFunction(me.viewer.refresh)) {
            me.viewer.refresh();
            me.setViewerSize();
        }

        if(me.viewer instanceof CodeMirror.MergeView) {
            me.setMergeViewSize();
        }
    },
    //
    setViewerSize: function() {
        var me = this;
        if(Ext.isFunction(me.viewer.setSize)) {
            me.viewer.setSize("100%", me.cmContainer.getHeight());
        }
    },
    //
    setMergeViewSize: function() {
        var me = this,
            cssMirror = Ext.util.CSS.getRule('.CodeMirror'),
            cssMerge = Ext.util.CSS.getRule('.CodeMirror-merge');
        if(cssMirror) {
            cssMirror.style.height = me.cmContainer.getHeight();
        }
        if(cssMerge) {
            cssMerge.style.height = me.cmContainer.getHeight();
        }
    },
    //
    initViewer: function() {
        var me = this,
            el = me.cmContainer.el.getById(me.id + '-cmEl', true);
        // Create CodeMirror
        me.viewer = new CodeMirror(el, {
            readOnly: true,
            lineNumbers: true,
            styleActiveLine: true
        });
        me.setTheme(me.preview_theme);
        me.viewer.setOption('mode', me.mode);
        me.sideBySideModeButton.toggle(false);
        CodeMirror.autoLoadMode(me.viewer, me.mode);
    },
    //
    removeViewer: function() {
        var me = this;
        me.removeAll();
        me.cmContainer = me.getCmContainer();
        me.insert(me.cmContainer);
    },
    // Set CodeMirror theme
    setTheme: function(name) {
        var me = this;
        if(name !== 'default') {
            Ext.util.CSS.swapStyleSheet(
                'cmcss-' + me.id,  // Fake one
                '/ui/pkg/codemirror/theme/' + name + '.css'
            );
        }
        me.viewer.setOption('theme', name);
    },
    //
    startPreview: function(record, backItem) {
        var me = this,
            bi = backItem === undefined ? me.backItem : backItem;
        me.currentRecord = record;
        me.backItem = bi;
        me.rootUrl = Ext.String.format(me.restUrl, record.get('id'));
        me.setTitle(Ext.String.format(me.previewName, record.get('name')));
        me.fileName = Ext.String.format("{0}_{1}", Ext.util.Format.lowercase(record.get('pool__label')), record.get('address'));
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.startPreview(record, backItem);
        me.requestText();
        me.requestRevisions();
    },
    //
    requestText: function() {
        var me = this,
            mask = me.setLoading({msg: 'Loading'});
        Ext.Ajax.request({
            url: me.rootUrl,
            method: 'GET',
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText));
                mask.hide();
            },
            failure: function() {
                mask.hide();
                NOC.error(__('Failed to get text'));
            }
        });
    },
    //
    requestRevisions: function(callback) {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl + 'revisions/',
            method: 'GET',
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);

                me.diffCombo.setValue(null);
                me.revCombo.setValue(null);
                me.sideBySideModeButton.toggle(false);
                me.revCombo.store.loadData(data);
                me.diffCombo.store.loadData(data);
                if(data.length > 0) {
                    me.revCombo.select([me.revCombo.store.getAt(0)]);
                }
                Ext.callback(callback, me);
            },
            failure: function() {
                NOC.error(__('Failed to get revisions'));
            }
        });
    },
    //
    requestRevision: function(rev) {
        var me = this,
            mask = me.setLoading({msg: 'Loading'});
        Ext.Ajax.request({
            url: me.rootUrl + rev + '/',
            method: 'GET',
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText));
                mask.hide();
            },
            failure: function() {
                NOC.error(__('Failed to get text'));
                mask.hide();
            }
        });
    },
    //
    requestDiff: function(rev1, rev2) {
        var me = this,
            mask = me.setLoading({msg: 'Loading'});
        if(me.sideBySideModeButton.pressed) {
            var getRev = function(id) {
                var deferred = new Ext.Deferred();

                Ext.Ajax.request({
                    url: me.rootUrl + id + '/',
                    method: 'GET',
                    scope: me,
                    success: function(response) {
                        deferred.resolve(Ext.decode(response.responseText));
                    },
                    failure: function() {
                        deferred.reject(__('Failed to get diff'));
                    }
                });
                return deferred.promise;
            };

            // ToDo refactor!
            getRev(rev1).then(function(rev1Text) {
                getRev(rev2).then(function(rev2Text) {
                        me.renderText(rev2Text, 'merge', rev1Text);
                        mask.hide();
                    }, function(error) {
                        NOC.error(error);
                        mask.hide();
                    }
                );
            }, function(error) {
                NOC.error(error);
                mask.hide();
            });
        } else {
            Ext.Ajax.request({
                url: me.rootUrl + rev1 + '/' + rev2 + '/',
                method: 'GET',
                scope: me,
                success: function(response) {
                    me.renderText(Ext.decode(response.responseText), 'diff');
                    mask.hide();
                },
                failure: function() {
                    NOC.error(__('Failed to get diff'));
                    mask.hide();
                }
            });
        }
    },
    //
    renderText: function(text, addon, left) {
        var me = this;
        addon = addon || null;
        text = text || 'NO DATA';
        if(addon === 'merge') {
            me.removeViewer();
            var el = me.cmContainer.el.getById(me.id + '-cmEl', true);
            var theme = me.preview_theme;

            if(theme !== 'default') {
                Ext.util.CSS.swapStyleSheet(
                    'cmcss-' + me.id,  // Fake one
                    '/ui/pkg/codemirror/theme/' + theme + '.css'
                );
            }
            me.viewer = CodeMirror.MergeView(el, {
                readOnly: false,
                lineNumbers: true,
                styleActiveLine: true,
                origLeft: left,
                revertButtons: false,
                allowEditingOriginals: true,
                value: text,
                theme: theme
            });
            CodeMirror.autoLoadMode(me.viewer, me.mode);
        } else {
            if(!Ext.isFunction(me.viewer.getMode)) {
                me.removeViewer();
                // save state
                var sp = me.sideBySideModeButton.pressed;
                me.initViewer();
                // restore
                me.sideBySideModeButton.toggle(sp);
            }
            me.viewer.setValue(text);
        }
        me.onResize();
    },
    //
    onSelectRev: function(combo, records, eOpts) {
        var me = this;
        me.requestRevision(records.get('id'));
    },
    //
    requestCurrentDiff: function() {
        var me = this;
        me.requestDiff(
            me.diffCombo.getValue(),
            me.revCombo.getValue()
        );
    },
    //
    onSelectDiff: function(combo, records, eOpts) {
        var me = this;
        me.requestCurrentDiff();
    },
    //
    onRevSpecialKey: function(combo, evt, opts) {
        var me = this;
        if(evt.getKey() === evt.ESC) {
            combo.clearValue();
        }
    },
    //
    onDiffSpecialKey: function(combo, evt, opts) {
        var me = this;
        if(evt.getKey() === evt.ESC) {
            combo.clearValue();
            me.requestRevision(me.revCombo.getPicker().getSelectionModel().lastSelected.get("id"));
        }
    },
    // Returns current selection index or null
    getRevIndex: function(combo) {
        var me = this,
            v = combo.getValue();
        return combo.store.findExact('id', v);
    },
    //
    setRevIndex: function(combo, index) {
        var me = this;
        combo.select([combo.store.getAt(index)]);
    },
    //
    onPrevDiff: function() {
        var me = this,
            rIndex = me.getRevIndex(me.revCombo),
            dIndex = me.getRevIndex(me.diffCombo);
        if(rIndex === dIndex - 1) {
            me.setRevIndex(me.revCombo, rIndex + 1);
            dIndex = rIndex + 2;
        } else {
            dIndex = rIndex + 1;
        }
        me.setRevIndex(me.diffCombo, dIndex);
        me.requestCurrentDiff();
    },
    //
    onNextDiff: function() {
        var me = this,
            rIndex = me.getRevIndex(me.revCombo),
            dIndex = me.getRevIndex(me.diffCombo);
        if(rIndex === dIndex - 1) {
            rIndex -= 1;
            me.setRevIndex(me.revCombo, rIndex);
        }
        dIndex = rIndex + 1;
        me.setRevIndex(me.diffCombo, dIndex);
        me.requestCurrentDiff();
    },
    //
    onSwapRev: function() {
        var me = this,
            rIndex = me.getRevIndex(me.revCombo),
            dIndex = me.getRevIndex(me.diffCombo);
        me.setRevIndex(me.revCombo, dIndex);
        me.setRevIndex(me.diffCombo, rIndex);
        me.requestCurrentDiff();
    },

    onReset: function() {
        var me = this;
        me.requestText();
        me.requestRevisions();
    },
    //
    getCmContainer: function() {
        var me = this;
        return Ext.create('Ext.container.Container', {
            tpl: [
                '<div id="{cmpId}-cmEl" class="{cmpCls}" style="{size}"></div>'
            ],
            data: {
                cmpId: me.id,
                cmpCls: Ext.baseCSSPrefix + 'codemirror ' + Ext.baseCSSPrefix + 'html-editor-wrap ' + Ext.baseCSSPrefix + 'html-editor-input',
                size: 'width:100%;height:100%'
            }
        });
    },
    //
    onBack: function() {
        var me = this;
        me.onClose();
    },
    //
    onSideBySide: function() {
        var me = this,
            ids = me.getIds();
        me.requestDiff(ids.leftId, ids.rightId);
    },
    //
    onDownload: function() {
        var me = this,
            blob = new Blob([me.viewer.getValue()], {type: "text/plain;charset=utf-8"}),
            suffix = me.revCombo.getDisplayValue().split(" ")[0].replace(/-/g, "") + ".conf.txt";
        saveAs(blob, me.fileName + "_" + suffix);
    },
    //
    getIds: function() {
        var me = this;
        return {
            leftId: me.revCombo.getValue(),
            rightId: me.diffCombo.getValue()
        };
    },
    //
    setLoading: function(cfg) {
        var me = this;
        return me.cmContainer.setLoading(cfg)
    }
});
