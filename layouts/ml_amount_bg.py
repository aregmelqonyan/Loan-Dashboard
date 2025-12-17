from dash import dcc, html

def create_loan_chart_layout(data_loader):
    """Create loan chart with its own grade and date filters inside"""
    
    min_date, max_date = data_loader.get_date_range() if data_loader else (None, None)
    all_grades = data_loader.get_unique_grades() if data_loader else []
    default_grades = [g for g in all_grades if g in ['A', 'B', 'C', 'D', 'E']]
    
    return html.Div(className="loan-chart-layout", children=[        
        html.Div(className="chart-filter-section", children=[
            html.Div(className="filter-row", children=[
                html.Div(className="filter-item", children=[
                    dcc.Dropdown(
                        id='loan-grade-filter',
                        options=[{'label': f'{g}', 'value': g} for g in all_grades],
                        value=default_grades,
                        multi=True,
                        placeholder="Select grades...",
                        className="chart-grade-dropdown"
                    )
                ]),
                
                html.Div(className="filter-item", children=[
                    dcc.DatePickerRange(
                        id='loan-date-filter',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=min_date,
                        end_date=max_date,
                        display_format='YYYY-MM-DD',
                        className="chart-date-filter"
                    )
                ]),
            ]),
        ]),
        
        html.Div(className="loan-chart-container", children=[
            dcc.Graph(
                id='loan-chart',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'loan_chart',
                        'height': 500,
                        'width': 800,
                        'scale': 2
                    }
                },
                className="loan-chart-graph"
            )
        ]),
        
        dcc.Store(id='loan-filter-state', data={
            'grades': default_grades,
            'start_date': str(min_date) if min_date else None,
            'end_date': str(max_date) if max_date else None
        })
    ])