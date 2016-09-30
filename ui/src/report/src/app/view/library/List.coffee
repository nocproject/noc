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
			emptyText: 'Пусто'
			deferEmptyText: false
		}
	]
	
	###
        Автоматический обработчик установки {@link #cfg-store}.
        Передает стор лежащему внутри вью, устанавливая его
        как источник данных для элементов списка.
        @param {Ext.data.Store} store Установленный стор.
	###
	updateStore: (store) ->
		@getListView().setStore store
	
	###
	    Возвращает выбранный элемент сущности из списка в виде модели
        либо null если ничего не выбрано.
        @return {Ext.data.Model/Null} Значение.
	###
	getSelected: () ->
		@getListView().getSelectionModel().getSelection()[0] or null
		
	privates:
		
		###
            @return {Ext.view.View} Вью выбора списка сущностей.
		###
		getListView: () ->
			@down('#view')