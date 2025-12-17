import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_daq as daq

def create_risk_subgrade_layout(data_loader):
    """Create layout for risk subgrade analysis section"""
    
    unique_grades = data_loader.get_unique_grades() if data_loader else []
    min_date, max_date = data_loader.get_date_range() if data_loader else (None, None)
    
    return html.Div(
        className="risk-subgrade-container",
        children=[            
            html.Div(
                className="simple-controls-row",
                children=[
                    html.Div(
                        className="simple-control-group",
                        children=[
                            dcc.DatePickerRange(
                                id='risk-date-filter',
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=max_date,
                                display_format='YYYY-MM-DD',
                                className="simple-date-picker"
                            )
                        ]
                    ),
                    
                    html.Div(
                        className="simple-control-group toggle-control",
                        children=[
                            daq.BooleanSwitch(
                                id='risk-group-toggle',
                                on=False,
                                label="Subgrade Mode",
                                labelPosition="right",
                                color="#1B5E20",
                                className="simple-toggle-switch"
                            )
                        ]
                    ),
                    
                    html.Div(
                        className="simple-control-group",
                        children=[
                            dcc.Dropdown(
                                id='risk-grade-filter',
                                options=[{'label': grade, 'value': grade} for grade in unique_grades],
                                placeholder="All grades",
                                className="simple-grade-dropdown"
                            )
                        ]
                    ),
                ]
            ),
            
            html.Div(
                className="graph-container",
                children=[
                    dcc.Graph(
                        id='risk-subgrade-chart',
                        className="risk-chart",
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': 'risk_subgrade_chart',
                                'height': 500,
                                'width': 800,
                                'scale': 2
                            }
                        }
                    ),
                    dcc.Store(id='risk-filter-state', data={}),
                    dcc.Store(id='summary-data-store', data={})
                ]
            ),
        ]
    )