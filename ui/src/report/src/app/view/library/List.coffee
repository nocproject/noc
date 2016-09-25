###
    Список сущностей конкретной библиотеку.
###
Ext.define 'Report.view.library.List',
	extend: 'Ext.container.Container'
	xtype: 'libraryList'
	
	layout: 'fit'
	padding: 20
	
	config:
	
		###
		    @cfg {Ext.data.Store} store Стор для списка сущностей.
		###
		store: null
	
	items: [
		{
			itemId: 'view'
			xtype: 'dataview'
			itemTpl: '<span class="item">{name}</span>'
		}
	]
	
	initComponent: () ->
		@callParent arguments
		
		@down('#view').setStore @getStore()