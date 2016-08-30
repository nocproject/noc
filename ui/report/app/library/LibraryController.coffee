Ext.define 'Report.library.LibraryController',
	extend: 'Ext.app.ViewController'
	alias: 'controller.library'
	requires: [
		'Report.data.MemoryStore'
	]

	config:
		libraryStore: null
		groupsStore: null

	constructor: () ->
		@callParent arguments

		@setLibraryStore @makeLibraryStore()
		@setGroupsStore @makeLibraryStore()
		@getLibraryStore().on 'load', @updateLibrary, @

		Report.data.Mediator.bindStore @getLibraryStore(), {method: 'widgetLibrary'}

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

	makeLibraryStore: () ->
		Ext.create 'Report.data.MemoryStore',
			model: 'Report.model.Library'

	addWidget: () ->
		@fireEvent 'addWidget', @, @getSelected()

	getSelected: () ->
		@getView().down('#widgets').getSelection()