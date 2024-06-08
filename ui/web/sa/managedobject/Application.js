//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

defaultColumns = [
  {
    xtype: 'glyphactioncolumn',
    width: 25,
    items: [{
      glyph: NOC.glyph.cart_plus,
      handler: 'onAddObject',
    }],
  },
  {
    text: __("S"),
    dataIndex: "oper_state",
    sortable: false,
    width: 30,
    renderer: function(value, metaData){
      var color = "grey";
      metaData.tdAttr = "data-qtip='<table style=\"font-size: 11px;\">" +
                "<tr><td style=\"padding-right: 10px;\"><div class=\"noc-object-oper-state\" style=\"background-color: grey;\"></div></td><td>" + __("Unmanaged or ping is disabled") + "</td></tr>" +
                "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: red;\"></div></td><td>" + __("Ping fail") + "</td></tr>" +
                "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: yellow;\"></div></td><td>" + __("Device has alarm") + "</td></tr>" +
                "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: green;\"></div></td><td>" + __("Device is normal") + "</td></tr>" +
                "</table>'";
      if(value === "failed"){
        color = "red";
      } else if(value === "degraded"){
        color = "yellow";
      } else if(value === "full"){
        color = "green";
      }
      return"<div class='noc-object-oper-state' style='background-color: " + color + "'></div>";
    },
  },
  {
    text: __('Name'),
    dataIndex: 'name',
    width: 200,
  },
  {
    text: __('Managed'),
    dataIndex: 'is_managed',
    width: 30,
    renderer: NOC.render.Bool,
  },
  {
    text: __("State"),
    dataIndex: "state",
  },
  {
    text: __('Address'),
    dataIndex: 'address',
    width: 100,
  },
  {
    text: __('Profile'),
    dataIndex: 'profile',
    width: 100,
  },
  {
    text: __('Platform'),
    dataIndex: 'platform',
    flex: 1,
  },
  {
    text: __('Version'),
    dataIndex: 'version',
    flex: 1,
  },
  {
    text: __('Obj. Profile'),
    dataIndex: 'object_profile',
    flex: 1,
  },
  {
    text: __('Adm. Domain'),
    dataIndex: 'administrative_domain',
    flex: 1,
  },
  {
    text: __('Auth Profile'),
    dataIndex: 'auth_profile',
    flex: 1,
  },
  {
    text: __('VRF'),
    dataIndex: 'vrf',
    flex: 1,
  },
  {
    text: __('Pool'),
    dataIndex: 'pool',
    flex: 1,
  },
  {
    text: __('Description'),
    dataIndex: 'description',
    flex: 1,
  },
  {
    text: __('Interfaces'),
    dataIndex: 'interface_count',
    width: 50,
    sortable: false,
    align: "right",
    renderer: function(value, metaData){
      metaData.tdStyle = "text-decoration-line: underline;cursor: pointer;";
      return value;
    },
  },
  {
    text: __('Links'),
    dataIndex: 'link_count',
    width: 50,
    sortable: true,
    align: "right",
    renderer: function(value, metaData){
      metaData.tdStyle = "text-decoration-line: underline;cursor: pointer;";
      return value;
    },
  },
  {
    text: __('Labels'),
    dataIndex: 'labels',
    renderer: NOC.render.LabelField,
    align: "right",
    width: 100,
  },
];
//
console.debug('Defining NOC.sa.managedobject.Application');
Ext.define('NOC.sa.managedobject.Application', {
  itemId: "sa-managedobject",
  extend: 'NOC.core.Application',
  layout: 'card',
  alias: 'widget.managedobject',
  viewModel: 'managedobject',
  controller: 'managedobject',
  requires: [
    'Ext.layout.container.Card',
    'Ext.form.field.ComboBox',
    'NOC.sa.managedobject.ViewModel',
    'NOC.sa.managedobject.Controller',
    'NOC.core.filter.Filter',
    'NOC.sa.managedobject.form.View',
  ],
  stateMap: {
    w: __('Waiting'),
    r: __('Running'),
    s: __('Success'),
    f: __('Failed'),
  },
  defaults: {
    xtype: 'panel',
    layout: 'border',
    border: false,
    scrollable: false,
  },
  items: [
    {
      itemId: 'managedobject-select',
      activeItem: 0,
      items: [
        {   // device panel
          xtype: 'panel',
          layout: 'border',
          region: 'center',
          border: false,
          scrollable: false,
          items: [
            {
              xtype: 'grid', // selection grid
              stateful: true,
              stateId: "sa.managedobject-selection-grid",
              reference: 'saManagedobjectSelectionGrid',
              region: 'center',
              width: '50%',
              resizable: true,
              pageSize: 0,
              border: false,
              scrollable: true,
              emptyText: __('Not Found'),
              columns: [{
                xtype: 'glyphactioncolumn',
                width: 50,
                items: [
                  {
                    glyph: NOC.glyph.star,
                    tooltip: __('Mark/Unmark'),
                    getColor: function(cls, meta, r){
                      return r.get("fav_status") ? NOC.colors.starred : NOC.colors.unstarred;
                    },
                    handler: 'onFavItem',
                  },
                  {
                    glyph: NOC.glyph.edit,
                    tooltip: __('Edit'),
                    handler: 'onEdit',
                  },
                ],
              }].concat(this.defaultColumns),
              bind: {
                store: '{selectionStore}',
                selection: '{selectionRow}',
              },
              selModel: {
                mode: 'MULTI',
                selType: 'checkboxmodel',
              },
              listeners: {
                selectionchange: 'onSelectionChange',
                itemdblclick: 'onSelectionDblClick',
                afterrender: 'setRowClass',
                cellclick: 'onCellClick',
              },
              dockedItems: [{
                tbar: {
                  items: [
                    { // @todo: Search
                      glyph: NOC.glyph.refresh,
                      tooltip: __('Refresh data'),
                      style: {
                        pointerEvents: 'all',
                      },
                      handler: 'onSelectionRefresh',
                    },
                    {
                      xtype: 'combo',
                      editable: false,
                      minWidth: 225,
                      emptyText: __('Group select'),
                      store: {
                        fields: ['cmd', 'title'],
                        data: [
                          {'cmd': 'SCREEN', 'title': __('All devices on screen')},
                          {'cmd': 'FIRST_50', 'title': __('First 50')},
                          {'cmd': 'FIRST_100', 'title': __('First 100')},
                          {'cmd': 'N_ROWS', 'title': __('First N')},
                          {'cmd': 'PERIOD', 'title': __('Period start,qty')},
                        ],
                      },
                      queryMode: 'local',
                      displayField: 'title',
                      valueField: 'cmd',
                      listeners: {
                        select: 'onSelectionSelectAll',
                      },
                    },
                    {
                      text: __('Unselect All'),
                      glyph: NOC.glyph.minus_circle,
                      tooltip: __('Unselect all devices'),
                      style: {
                        pointerEvents: 'all',
                      },
                      bind: {
                        disabled: '{!selectionGridHasSel}',
                      },
                      handler: 'onSelectionUnselectAll',
                    },
                    '->',
                    {
                      text: __('Add'),
                      glyph: NOC.glyph.cart_plus,
                      tooltip: __('Move all selected devices to the basket'),
                      style: {
                        pointerEvents: 'all',
                      },
                      bind: {
                        disabled: '{!selectionGridHasSel}',
                      },
                      handler: 'onSelectionAddChecked',
                    },
                    '|',
                    {
                      glyph: NOC.glyph.shopping_cart,
                      tooltip: __('Show/Hide Basket'),
                      style: {
                        pointerEvents: 'all',
                      },
                      bind: {
                        disabled: '{!hasRecords}',
                        text: '{total.selected}',
                        style: {
                          cursor: '{cursorIcon}',
                        },
                      },
                      handler: 'toggleBasket',
                    },
                    '|',
                    {
                      glyph: NOC.glyph.trash_o,
                      tooltip: __('Clean Basket'),
                      style: {
                        pointerEvents: 'all',
                      },
                      bind: {
                        disabled: '{!hasRecords}',
                        style: {
                          cursor: '{cursorIcon}',
                        },
                      },
                      handler: 'onSelectedRemoveAll',
                    },
                    '|',
                    {
                      xtype: 'box',
                      bind: {
                        html: '<span class="x-btn-inner x-btn-inner-default-toolbar-small">' + __('Selected : {total.selection}') + '</span',
                      },
                    },
                    '|',
                    {
                      xtype: 'box',
                      bind: {
                        html: '<span class="x-btn-inner x-btn-inner-default-toolbar-small">' + __('Total : {total.all}') + '</span>',
                      },
                    }],
                },
              }],
              viewConfig: {
                enableTextSelection: true,
              },
            },
            {
              xtype: 'grid', // selected grid
              stateful: true,
              stateId: "sa.managedobject-selected1-grid",
              reference: 'saManagedobjectSelectedGrid1',
              region: 'east',
              width: '50%',
              collapsed: true,
              animCollapse: false,
              collapseMode: 'mini',
              hideCollapseTool: true,
              resizable: true,
              pageSize: 0,
              border: false,
              scrollable: true,
              emptyText: __('nothing checked'),
              columns: [{
                xtype: 'glyphactioncolumn',
                width: 25,
                items: [{
                  glyph: NOC.glyph.minus_circle,
                  handler: 'onRemoveObject',
                }],
              }].concat(this.defaultColumns),
              split: {
                xtype: 'splitter',
              },
              bind: {
                store: '{selectedStore}',
                selection: '{selectedRow}',
              },
              listeners: {
                itemdblclick: 'onSelectedDblClick',
                afterrender: 'setRowClass',
              },
              dockedItems: [{
                tbar: {
                  items: [{
                    text: __('Remove All'),
                    glyph: NOC.glyph.minus_circle,
                    tooltip: __('Remove all devices from right panel'),
                    style: {
                      pointerEvents: 'all',
                    },
                    bind: {
                      disabled: '{!hasRecords}',
                      style: {
                        cursor: '{cursorIcon}',
                      },
                    },
                    handler: 'onSelectedRemoveAll',
                  },
                          {
                            text: __('Export'),
                            glyph: NOC.glyph.arrow_down,
                            tooltip: __("Save all from basket"),
                            handler: 'onExportBasket',

                          },
                          '->',
                          {
                            xtype: 'container',
                            glyph: NOC.glyph.shopping_cart,
                            bind: {
                              html: '<span class="x-btn-button x-btn-button-default-toolbar-small x-btn-text x-btn-icon x-btn-icon-left x-btn-button-center">'
                                                + '<span class="x-btn-icon-el x-btn-icon-el-default-toolbar-small x-btn-glyph" style="font-family:FontAwesome;">&#xf07a;</span>'
                                                + '<span class="x-btn-inner x-btn-inner-default-toolbar-small">' + __('Total : {total.selected}') + '</span>'
                                                + '</span>',
                            },
                          }],
                },
              }],
              title: __('Basket'),
              tools: [
                {
                  type: 'right',
                  tooltip: __('Hide basket'),
                  callback: 'toggleBasket',
                },
              ],
            },
          ],
        },
        {
          xtype: 'NOC.Filter',
          reference: 'filterPanel',
          region: 'east',
          width: 300,
          collapsed: true,
          border: false,
          animCollapse: false,
          collapseMode: 'mini',
          hideCollapseTool: true,
          split: {
            xtype: 'splitter',
          },
          treeAlign: 'left',
          resizable: true,
          selectionStore: 'managedobject.selectionStore',
          listeners: {
            changeSearchField: function(){
              console.log('changeSearchField');
            },
          },
        },
      ],
      dockedItems: [{
        tbar: {
          items: [
            {
              xtype: 'searchfield',
              itemId: '__query',  // name of http request query param
              width: 400,
              emptyText: __('Search ...'),
              triggers: {
                clear: {
                  cls: 'x-form-clear-trigger',
                  handler: 'cleanSearchField',
                },
              },
              listeners: {
                specialkey: 'onSearchFieldChange',
              },
            }, '|', {
              text: __('Filtering List'),
              glyph: NOC.glyph.filter,
              tooltip: __('Show/Hide Filter'),
              style: {
                pointerEvents: 'all',
              },
              handler: 'collapseFilter',
            }, {
              xtype: 'splitbutton',
              text: __('Group Operation'),
              tooltip: __('Select Action'),
              bind: {
                disabled: '{!hasRecords}',
              },
              menu: {
                items: [
                  {
                    text: __("Group Edit"),
                    glyph: NOC.glyph.edit,
                    bind: {
                      disabled: '{!hasUpdatePerm}',
                    },
                    handler: 'onGroupEdit',
                  },
                  {
                    text: __("Run discovery now"),
                    glyph: NOC.glyph.play,
                    handler: "onRunDiscovery",
                  },
                  {
                    text: __("Set managed"),
                    glyph: NOC.glyph.check,
                    handler: "onSetManaged",
                  },
                  {
                    text: __("Set unmanaged"),
                    glyph: NOC.glyph.times,
                    handler: "onSetUnmanaged",
                  },
                  {
                    text: __("New Maintaince"),
                    glyph: NOC.glyph.wrench,
                    handler: "onNewMaintaince",
                  },
                  {
                    text: __("Add to Maintaince"),
                    glyph: NOC.glyph.plus,
                    handler: "onAddToMaintaince",
                  },
                  {
                    itemId: "runCmdBtn",
                    text: __("Run Commands"),
                    glyph: NOC.glyph.play,
                    bind: {
                      disabled: '{!hasRunCmdPerm}',
                    },
                    handler: "toNext",
                  },
                ],
              },
            }, {
              itemId: "createBtn",
              text: __("Add"),
              glyph: NOC.glyph.plus,
              tooltip: __("Add new record"),
              bind: {
                disabled: '{!hasCreatePerm}',
              },
              handler: "onNewRecord",
            },
          ],
        },
      }],
    },
    {
      itemId: 'managedobject-config',
      activeItem: 1,
      items: [
        {
          xtype: 'grid',
          reference: 'saManagedobjectSelectedGrid2',
          region: 'center',
          width: '50%',
          border: false,
          scrollable: true,
          bind: '{selectedStore}',
          columns: this.defaultColumns.concat([{
            xtype: 'glyphactioncolumn',
            width: 25,
            items: [{
              glyph: NOC.glyph.minus_circle,
              handler: 'onRemoveObject',
            }],
          }]),
          listeners: {
            afterrender: 'setRowClass',
          },
        },
        {
          xtype: 'panel',
          region: 'east',
          width: '50%',
          border: false,
          defaults: {
            padding: 4,
            width: '80%',
          },
          items: [
            {
              xtype: 'panel',
              border: false,
              defaults: {
                padding: 10,
              },
              layout: {
                type: 'hbox',
                align: 'middle',
              },
              items: [
                {
                  xtype: 'checkboxfield',
                  reference: 'ignoreCliErrors',
                  boxLabel: __('Ignore CLI errors'),
                  checked: true,
                },
                {
                  xtype: 'combo',
                  reference: 'saManagedobjectMode',
                  fieldLabel: __('Mode'),
                  labelWidth: 50,
                  queryMode: 'local',
                  displayField: 'name',
                  valueField: 'value',
                  editable: false,
                  store: {
                    data: [
                      {value: 'commands', name: __('Run Commands')},
                      {value: 'snippet', name: __('Run Snippet')},
                      {value: 'action', name: __('Run Action')},
                    ],
                  },
                  listeners: {
                    change: 'onConfigModeChange',
                    afterrender: function(field){
                      field.setValue('commands');
                    },
                  },
                },
              ],
            },
            {
              xtype: 'form',
              reference: 'saManagedobjectCommandForm',
              width: '100%',
              border: false,
              defaults: {
                margin: 10,
                padding: 20,
                width: '80%',
              },
              bind: {
                disabled: '{!hasRecords}',
              },
              dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                ui: 'header',
                defaults: {minWidth: '<a href="#cfg-minButtonWidth">minButtonWidth</a>'},
                items: [
                  {xtype: 'component', flex: 1},
                  {
                    xtype: 'button', text: __('Run'),
                    glyph: NOC.glyph.play,
                    disabled: true,
                    formBind: true,
                    handler: 'onRun',
                  },
                ],
              }],
            },
          ],
        },
      ],
      dockedItems: [{
        tbar: {
          items: [
            {
              glyph: NOC.glyph.arrow_left,
              tooltip: __('Back'),
              style: {
                pointerEvents: 'all',
              },
              handler: 'toPrev',
            },
          ],
        },
      }],
    },
    {
      itemId: 'run-command-progress',
      activeItem: 2,
      items: [
        {
          xtype: 'grid',
          reference: 'saManagedobjectSelectedGrid3',
          region: 'center',
          width: '50%',
          border: false,
          scrollable: true,
          bind: '{selectedStore}',
          columns: this.defaultColumns.concat({
            text: __('Status'),
            dataIndex: 'status',
            width: 70,
            renderer: NOC.render.Choices({
              w: __('Waiting'),
              r: __('Running'),
              f: __('Failed'),
              s: __('Success'),
            }),
          }),
          selModel: {
            mode: 'SINGLE',
            selType: 'checkboxmodel',
          },
          listeners: {
            afterrender: 'setStatusClass',
            select: 'onShowResult',
          },
          dockedItems: [{
            xtype: 'toolbar',
            dock: 'top',
            items: {
              xtype: 'segmentedbutton',
              height: 25,
              columns: 4,
              frame: false,
              allowMultiple: true,
              items: [
                {
                  pressed: true,
                  value: 'w',
                  bind: {
                    text: '<span>' + __('Waiting') + '&nbsp;<span class="noc-badge noc-badge-waiting">{progressState.w}</span></span>',
                  },
                },
                {
                  pressed: true,
                  value: 'r',
                  bind: {
                    text: '<span>' + __('Running') + '&nbsp;<span class="noc-badge noc-badge-running">{progressState.r}</span></span>',
                  },
                },
                {
                  pressed: true,
                  value: 'f',
                  bind: {
                    text: '<span>' + __('Failed') + '&nbsp;<span class="noc-badge noc-badge-failed">{progressState.f}</span></span>',
                  },
                },
                {
                  pressed: true,
                  value: 's',
                  bind: {
                    text: '<span>' + __('Success') + '&nbsp;<span class="noc-badge noc-badge-success">{progressState.s}</span></span>',
                  },
                },
              ],
              listeners: {
                toggle: 'onStatusToggle',
              },
            },
          }],
        },
        {
          xtype: 'panel',
          region: 'east',
          width: '50%',
          scrollable: true,
          padding: 4,
          items: {
            xtype: 'container',
            layout: 'fit',
            fieldStyle: {
              'fontFamily': 'courier new',
              'fontSize': '12px',
            },
            bind: {
              html: '{resultOutput}',
            },
          },
        },
      ],
      dockedItems: [{
        tbar: {
          items: [
            {
              glyph: NOC.glyph.arrow_left,
              tooltip: __('Back'),
              style: {
                pointerEvents: 'all',
              },
              handler: 'toPrev',
              bind: {
                disabled: '{isRunning}',
              },
            }, {
              glyph: NOC.glyph.print,
              tooltip: __('Report'),
              style: {
                pointerEvents: 'all',
              },
              bind: {
                disabled: '{isRunning}',
              },
              handler: 'onReportClick',
            },
          ],
        },
      }],
    },
    {
      itemId: 'run-command-report',
      activeItem: 3,
      xtype: 'panel',
      reference: 'saRunCommandReportPanel',
      html: '',
      scrollable: true,
      bodyPadding: 4,
      dockedItems: [{
        xtype: 'toolbar',
        dock: 'top',
        items: [
          {
            glyph: NOC.glyph.arrow_left,
            tooltip: __('Back'),
            style: {
              pointerEvents: 'all',
            },
            handler: 'toPrev',
          },
          {
            glyph: NOC.glyph.download,
            tooltip: __('Download results'),
            style: {
              pointerEvents: 'all',
            },
            handler: 'onDownload',
          },
        ],
      }],
    },
    {
      activeItem: 4,
      itemId: 'managedobject-form',
      items: [
        {
          xtype: 'managedobject.form',
        },
      ],
    },
  ],
  destroy: Ext.emptyFn,
  // Used inv.inv tab ManagedObject 
  loadById: function(id){
    var me = this;
    me.getController().editManagedObject(undefined, id, undefined, true);
  },
});
