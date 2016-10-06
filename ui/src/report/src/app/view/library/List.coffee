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
			selectionModel:
				mode: 'MULTI'
		}
	]
	
	initComponent: () ->
		@callParent arguments
		
		@on 'afterrender', @fireEventOnSelectEntity.bind @
	
	###
        Автоматический обработчик установки {@link #cfg-store}.
        Передает стор лежащему внутри вью, устанавливая его
        как источник данных для элементов списка.
        @param {Ext.data.Store} store Установленный стор.
	###
	updateStore: (store) ->
		@getListView().setStore store
	
	###
	    Возвращает выбранный элемент сущности из списка
		в виде массива моделей.
        @return {Ext.data.Model[]} Значение.
	###
	getSelected: () ->
		@getListView().getSelectionModel().getSelection()
	
	###
		Выделяет свежесозданную сущность.
	###
	selectNew: () ->
		@getListView().select @getStore().last()
		
	privates:
		
		###
            Бросает эвент {@link #event-select} при выборе сущности в списке сущностей библиотеки.
        ###
		fireEventOnSelectEntity: () ->
			@getListView().on 'select', (selection, record) =>
				
				###
					@event select
					Оповещает о выборе сущности в списке сущностей библиотеки.
					@param {Report.view.library.List} this Виджет списка сущностей.
					@param {Ext.data.Record} record Данные сущности.
				###
				@fireEvent 'select', @, record
	
		###
            @return {Ext.view.View} Вью выбора списка сущностей.
		###
		getListView: () ->
			@down('#view')