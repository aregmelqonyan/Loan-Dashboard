from dash import dcc, html

def create_sunburst_layout(data_loader):
    """Create sunburst chart layout for risk groups and subgrades"""
    
    min_date, max_date = data_loader.get_date_range() if data_loader else (None, None)
    
    return html.Div(className="sunburst-chart-layout", children=[
        html.Div(className="chart-filter-section", children=[
            html.Div(className="filter-row", children=[
                html.Div(className="filter-item", children=[
                    dcc.DatePickerRange(
                        id='sunburst-date-filter',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=min_date,
                        end_date=max_date,
                        display_format='YYYY-MM-DD',
                        className="sunburst-date-filter"
                    )
                ]),
            ]),
        ]),
        
        html.Div(className="sunburst-chart-container", children=[
            dcc.Graph(
                id='sunburst-chart',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'risk_sunburst_chart',
                        'height': 500,
                        'width': 800,
                        'scale': 2
                    }
                },
                className="sunburst-chart-graph"
            )
        ]),
        
        dcc.Store(id='sunburst-filter-state', data={
            'start_date': str(min_date) if min_date else None,
            'end_date': str(max_date) if max_date else None
        })
    ])