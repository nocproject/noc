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
    historyHashPrefix: null,
    // preview_theme: NOC.settings.preview_theme,
    preview_theme: 'monokai',
    mode: 'groovy',

    initComponent: function() {
        var me = this;

        // me.revSlider = Ext.create('NOC.core.RevisionSlider', {
        //     label: __('Version'),
        //     labelWidth: 45,
        //     onChange: Ext.bind(me.onSlideRev, me),
        //     width: 200
        // });
        //
        // me.diffSlider = Ext.create('NOC.core.RevisionSlider', {
        //     label: __('Compare'),
        //     labelWidth: 55,
        //     onChange: Ext.bind(me.onSlideDiff, me),
        //     width: 200
        // });

        // me.compareModeButton = Ext.create("Ext.button.Button", {
        //     text: __("Compare Mode"),
        //     tooltip: __("Switch on/off compare mode"),
        //     enableToggle: true,
        //     pressed: false,
        //     scope: me,
        //     handler: me.onCompare
        // });

        me.sideBySideModeButton = Ext.create('Ext.button.Button', {
            text: __('Side-By-Side'),
            tooltip: __('Switch on/off side-by-side mode'),
            enableToggle: true,
            pressed: false,
            disabled: true,
            scope: me,
            handler: me.onSideBySide
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
            }
        });

        me.diffCombo = Ext.create('Ext.form.ComboBox', {
            fieldLabel: __('Compare'),
            disabled: true,
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
            }
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
            disabled: true,
            scope: me,
            handler: me.onNextDiff
        });
        //
        me.prevDiffButton = Ext.create('Ext.button.Button', {
            glyph: NOC.glyph.arrow_down,
            tooltip: __('Previous change'),
            disabled: true,
            scope: me,
            handler: me.onPrevDiff
        });
        //
        me.swapRevButton = Ext.create('Ext.button.Button', {
            glyph: NOC.glyph.exchange,
            tooltip: __('Swap revisions'),
            disabled: true,
            scope: me,
            handler: me.onSwapRev
        });
        //
        // me.lastDayButton = Ext.create("Ext.button.Button", {
        //     text: __("Day"),
        //     tooltip: __("Last day's changes"),
        //     toogleGroup: "diffrange",
        //     scope: me,
        //     handler: me.onLastPressed,
        //     diffRange: 1
        // });
        //
        // me.lastWeekButton = Ext.create("Ext.button.Button", {
        //     text: __("Week"),
        //     tooltip: __("Last week's changes"),
        //     toogleGroup: "diffrange",
        //     scope: me,
        //     handler: me.onLastPressed,
        //     diffRange: 7
        // });
        //
        // me.lastMonthButton = Ext.create("Ext.button.Button", {
        //     text: __("Month"),
        //     tooltip: __("Last month's changes"),
        //     toogleGroup: "diffrange",
        //     scope: me,
        //     handler: me.onLastPressed,
        //     diffRange: 30
        // });

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
                    // me.revSlider,
                    '-',
                    me.swapRevButton,
                    // me.compareModeButton,
                    '-',
                    me.diffCombo,
                    // me.diffSlider,
                    '-',
                    me.nextDiffButton,
                    me.prevDiffButton,
                    me.sideBySideModeButton
                    // me.lastDayButton,
                    // me.lastWeekButton,
                    // me.lastMonthButton
                    // "->",
                    // me.diffCombo,
                    // me.nextDiffButton,
                    // me.prevDiffButton
                ]
            }],
            items: [me.cmContainer],
            listeners: {
                scope: me,
                resize: me.onResize
            }
        });
        me.callParent();
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent(arguments);
        me.initViewer();
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
        // change the codemirror css
        var css = Ext.util.CSS.getRule('.CodeMirror');
        if(css) {
            css.style.height = '100%';
            css.style.position = 'relative';
            css.style.overflow = 'hidden';
        }
        css = Ext.util.CSS.getRule('.CodeMirror-Scroll');
        if(css) {
            css.style.height = '100%';
        }
        me.setTheme(me.preview_theme);
        me.viewer.setOption('mode', me.mode);
        me.sideBySideModeButton.setDisabled(true);
        // me.compareModeButton.toggle(false);
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
                // if(me.historyHashPrefix) {
                //     me.app.setHistoryHash(
                //         me.currentRecord.get("id"),
                //         me.historyHashPrefix
                //     );
                // }
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
                // console.log(me.revCombo.getValue());
                // console.log(me.diffCombo.getValue());
                me.revCombo.store.loadData(data);
                me.diffCombo.store.loadData(data);
                if(data.length > 0) {
                    me.revCombo.select([me.revCombo.store.getAt(0)]);
                }
                me.nextDiffButton.setDisabled(true);
                me.prevDiffButton.setDisabled(data.length === 1);

                // me.revSlider.setStore(data);
                // me.diffSlider.setStore(data);
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
                // if(me.historyHashPrefix) {
                //     me.app.setHistoryHash(
                //         me.currentRecord.get("id"),
                //         me.historyHashPrefix,
                //         rev
                //     );
                // }
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
                    // if(me.historyHashPrefix) {
                    //     me.app.setHistoryHash(
                    //         me.currentRecord.get("id"),
                    //         me.historyHashPrefix,
                    //         rev1,
                    //         rev2
                    //     );
                    // }
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
                viewportMargin: Infinity,
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
                var sd = me.sideBySideModeButton.disabled;
                var sp = me.sideBySideModeButton.pressed;
                // var cp = me.compareModeButton.pressed;
                me.initViewer();
                // restore
                me.sideBySideModeButton.setDisabled(sd);
                me.sideBySideModeButton.toggle(sp);
                // me.compareModeButton.toggle(cp);
            }
            me.viewer.setValue(text);
        }
    },
    //
    onSelectRev: function(combo, records, eOpts) {
        var me = this;
        me.requestRevision(records.get('id'));
        me.diffCombo.setDisabled(false);
        me.swapRevButton.setDisabled(false);
        me.sideBySideModeButton.setDisabled(false);
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
        me.sideBySideModeButton.setDisabled(false);
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
            me.onSelectRev(me.revCombo, [me.revCombo.picker.getSelectionModel().lastSelected]);
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
        me.sideBySideModeButton.setDisabled(false);
        me.setRevIndex(me.diffCombo, dIndex);
        me.prevDiffButton.setDisabled(dIndex >= me.revCombo.store.data.length - 1);
        me.nextDiffButton.setDisabled(false);
        me.diffCombo.setDisabled(false);
        me.swapRevButton.setDisabled(false);
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
        me.sideBySideModeButton.setDisabled(false);
        me.setRevIndex(me.diffCombo, dIndex);
        me.prevDiffButton.setDisabled(false);
        me.nextDiffButton.setDisabled(rIndex <= 0);
        me.diffCombo.setDisabled(false);
        me.swapRevButton.setDisabled(false);
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
    //
    // onLastPressed: function(button, evt) {
    //     var me = this,
    //         store = me.revCombo.store,
    //         rl = store.data.length - 1,
    //         i0 = me.getRevIndex(me.revCombo),
    //         t0 = i0 === 0 ? +(new Date()) : +store.getAt(0).get("ts"),
    //         t1 = t0 - button.diffRange * 86400000,
    //         i1;
    //     if(i0 === 0 && +store.getAt(0).get("ts") <= t1) {
    //         NOC.info(__("Nothing changed"));
    //         return;
    //     }
    //     for(i1 = i0 + 1; i1 < rl; i1++) {
    //         if(+store.getAt(i1).get("ts") <= t1)
    //             break;
    //     }
    //     me.setRevIndex(me.revCombo, i0);
    //     me.diffCombo.setDisabled(false);
    //     me.swapRevButton.setDisabled(false);
    //     me.setRevIndex(me.diffCombo, i1);
    //     me.requestCurrentDiff();
    // },
    //
    onReset: function() {
        var me = this;
        me.requestText();
        me.requestRevisions();
    },
    //
    // historyRevision: function(record, rev) {
    //     var me = this;
    //     me.startPreview(record);
    //     me.requestRevisions(function() {
    //         me.setRevIndex(
    //             me.revCombo,
    //             me.revCombo.store.findExact("id", rev)
    //         );
    //         me.diffCombo.setDisabled(false);
    //     });
    //     me.requestRevision(rev);
    // },
    // //
    // historyDiff: function(record, rev1, rev2) {
    //     var me = this;
    //     me.startPreview(record);
    //     me.requestRevisions(function() {
    //         me.diffCombo.setDisabled(false);
    //         me.setRevIndex(
    //             me.revCombo,
    //             me.revCombo.store.findExact("id", rev2)
    //         );
    //         me.setRevIndex(
    //             me.diffCombo,
    //             me.diffCombo.store.findExact("id", rev1)
    //         );
    //     });
    //     me.requestDiff(rev1, rev2);
    // },
    //
    onResize: function() {
        var me = this;
        if(me.viewer) {
            me.viewer.refresh();
        }
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
    // onSlideRev: function() {
    //     var me = this,
    //         ids = me.getIds();
    //     if(me.compareModeButton.pressed) {
    //         me.requestDiff(ids.leftId, ids.rightId);
    //     } else {
    //         me.requestRevision(ids.leftId);
    //     }
    // },
    // //
    // onSlideDiff: function(slider, value) {
    //     var me = this,
    //         ids = me.getIds();
    //     me.compareModeButton.toggle(true);
    //     me.sideBySideModeButton.setDisabled(false);
    //     me.requestDiff(ids.leftId, ids.rightId);
    // },
    //
    onBack: function() {
        var me = this;
        // me.revSlider.slider.fireEvent('hideTip');
        // me.diffSlider.slider.fireEvent('hideTip');
        me.onClose();
    },
    //
    // onCompare: function() {
    //     var me = this,
    //         ids = me.getIds();
    //     if(me.compareModeButton.pressed) {
    //         me.requestDiff(ids.leftId, ids.rightId);
    //         me.sideBySideModeButton.setDisabled(false);
    //     } else {
    //         me.sideBySideModeButton.setDisabled(true);
    //         me.requestRevision(ids.leftId);
    //     }
    // },
    onSideBySide: function() {
        var me = this,
            ids = me.getIds();
        me.requestDiff(ids.leftId, ids.rightId);
    },
    //
    getIds: function() {
        var me = this;
        return {
            leftId: me.revCombo.getValue(),
            rightId: me.diffCombo.getValue()
            // rightId: me.diffSlider.getRevId(),
            // leftId: me.revSlider.getRevId()
        };
    }
});
