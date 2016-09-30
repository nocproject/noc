###
	Окно библиотеки.
###
Ext.define 'Report.view.library.Main',
	extend: 'Report.view.ui.PopUpWindow'
	xtype: 'libraryMain'
	
	requires: [
		'Report.view.library.Control'
		'Report.view.library.Description'
		'Report.view.library.List'
	]
	
	width: 900
	height: 500
	layout: 'hbox'
	
	config:
	
		###
			@cfg {Object} store Конфигурация стора для библиотеки.
		###
		store: null
	
	items: [
		{
			itemId: 'list'
			xtype: 'libraryList'
			height: '100%'
			flex: 1
		}
		{
			itemId: 'description'
			xtype: 'libraryDescription'
			height: '100%'
			flex: 2
		}
	]
	
	dockedItems: [
		{
			itemId: 'control'
			xtype: 'libraryControl'
			dock: 'bottom'
		}
	]
	
	initComponent: () ->
		@callParent arguments
		
		store = Ext.create 'Ext.data.Store', @getStore()
		
		@down('#list').setStore store