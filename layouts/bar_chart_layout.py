from dash import dcc, html

def create_bar_chart_layout(data_loader):
    """Create horizontal bar chart layout for purpose, home_ownership, emp_length"""
    
    min_date, max_date = data_loader.get_date_range() if data_loader else (None, None)
    
    bar_variables = [
        {'label': 'Purpose', 'value': 'purpose'},
        {'label': 'Home Ownership', 'value': 'home_ownership'},
        {'label': 'Employment Length', 'value': 'emp_length'}
    ]
    
    return html.Div(className="bar-chart-layout", children=[
        html.Div(className="chart-filter-section", children=[
            html.Div(className="filter-row", children=[
                html.Div(className="filter-item", children=[
                    dcc.Dropdown(
                        id='bar-variable-filter',
                        options=bar_variables,
                        value='purpose',
                        clearable=False,
                        className="bar-variable-dropdown"
                    )
                ]),
                
                html.Div(className="filter-item date-filter-item", children=[
                    dcc.DatePickerRange(
                        id='bar-date-filter',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=min_date,
                        end_date=max_date,
                        display_format='YYYY-MM-DD',
                        className="bar-date-filter"
                    )
                ]),
            ]),
        ]),
        
        html.Div(className="bar-chart-container", children=[
            dcc.Graph(
                id='bar-chart',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'bar_chart_analysis',
                        'height': 500,
                        'width': 800,
                        'scale': 2
                    }
                },
                className="bar-chart-graph"
            )
        ]),
        
        dcc.Store(id='bar-filter-state', data={
            'variable': 'purpose',
            'start_date': str(min_date) if min_date else None,
            'end_date': str(max_date) if max_date else None
        })
    ])