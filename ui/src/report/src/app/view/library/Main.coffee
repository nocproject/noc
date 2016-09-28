###
	Окно библиотеки.
###
Ext.define 'Report.view.library.Main',
	extend: 'Ext.window.Window'
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
			flex: 1
		}
		{
			itemId: 'description'
			xtype: 'libraryDescription'
			flex: 2
		}
	]
	
	dockedItems: [
		{
			itemId: 'control'
			xtype: 'libraryControl'
		}
	]
	
	initComponent: () ->
		@callParent arguments
		
		store = Ext.create 'Ext.data.Store', @getStore()
		
		@down('#list').setStore store