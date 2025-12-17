from dash import dcc, html
import dash_bootstrap_components as dbc

def create_layout(data_loader):
    """Create layout with filters and two charts side by side"""
    
    min_date, max_date = data_loader.get_date_range() if data_loader else (None, None)
    all_grades = data_loader.get_unique_grades() if data_loader else []
    default_grades = [g for g in all_grades if g in ['A', 'B', 'C', 'D', 'E']]
    
    return html.Div([
        html.Div(className="filter-container", children=[
            html.Div(className="filter-wrapper", children=[
                dcc.Dropdown(
                    id='grade-selector',
                    options=[{'label': f'{g}', 'value': g} for g in all_grades],
                    value=default_grades,
                    multi=True,
                    className="grade-dropdown"
                ),
            ]),
            
            html.Div(className="filter-wrapper", children=[
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    start_date=min_date,
                    end_date=max_date,
                    display_format='YYYY-MM-DD',
                    className="w-100"
                ),
            ]),
        ]),
        
        html.Div(className="chart-container", children=[
            html.Div(className="chart-wrapper", children=[
                dcc.Graph(
                    id='loan-chart',
                    config={'displayModeBar': True}
                )
            ]),
            
            html.Div(className="chart-wrapper", children=[
                html.H3("Second Chart", className="chart-title"),
                dcc.Graph(
                    id='second-chart',
                    config={'displayModeBar': True}
                )
            ]),
        ]),
    ])