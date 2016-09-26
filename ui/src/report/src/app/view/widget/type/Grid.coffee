###
	Виджет для отображения табличных данных.
###
Ext.define 'Report.view.widget.type.Grid',
	extend: 'Report.view.widget.type.Abstract'
	xtype: 'widgetTypeGrid'
	 
	initComponent: () ->
		@callParent arguments
		
		@add {
			xtype: 'grid'
			store: @getStore()
			columns: @makeGridColumns()
		}
	
	privates:
		
		###
			Конструирует колонки для грида на основе колонок данных.
		###
		makeGridColumns: () ->
			@getColumns().getRange().map (column) ->
				{
					dataIndex: column.get 'id'
					text:      column.get 'title'
					flex: 1
				}