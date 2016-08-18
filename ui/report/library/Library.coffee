Ext.define 'Report.library.Library',
	extend: 'Ext.window.Window'
	xtype: 'library'
	cls: 'library'

	title: 'Библиотека виджетов'

	layout: 'hbox'
	width: 900
	height: 550
	closeAction: 'hide'

	items: [
		{
			itemId: 'groups'
			xtype: 'dataview'
			itemTpl: '<span class="item">{groupName}</span>'
			flex: 1

		}
		{
			itemId: 'widgets'
			xtype: 'dataview'
			itemTpl: '<span class="item">{name}</span>'
			flex: 1
		}
		{
			xtype: 'container'
			layout: 'vbox'
			flex: 2
			items: [
				{
					itemId: 'description'
					xtype: 'component'
					flex: 1
					tpl:
						'
						<div class="title">{name}</div>
						<div class="description">{description}</div>
						'
				}
				{
					xtype: 'button'
					text: 'Добавить'
					width: 100
					handler: 'addWidget'
				}
			]
		}
	]

	config:
		store: null
		groupsStore: null

	constructor: () ->
		@callParent arguments

		@setStore @makeStore()
		@setGroupsStore @makeStore()
		@getStore().on 'load', @updateLibrary, @

		Report.data.Mediator.bindStore store, {method: 'widgetLibrary'}

	updateLibrary: (store) ->
		@setLoading true

		collection = {}
		groupData = []

		store.each (record) ->
			data = record.getData()
			collection[data.groupName] = true

		for name of collection
			groupData.push {groupName: name}

		@getGroupsStore.loadData groupData

		@setLoading false

	makeStore: () ->
		Ext.create 'Report.data.MemoryStore',
			model: 'Report.model.Library'

	addWidget: () ->
        @fireEvent 'addWidget', @, @getSelected()

	getSelected: () ->
        @down('#widgets').getSelection()