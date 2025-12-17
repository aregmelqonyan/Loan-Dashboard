from dash import dcc, html
from layouts.ml_amount_bg import create_loan_chart_layout
from layouts.second import create_second_chart_layout
from layouts.risk_subgrade_layout import create_risk_subgrade_layout
from layouts.sunburst_layout import create_sunburst_layout  
from layouts.bar_chart_layout import create_bar_chart_layout  

def create_dashboard_layout(data_loader, extra_sections=None):
    
    risk_subgrade_section = create_risk_subgrade_layout(data_loader)
    sunburst_section = create_sunburst_layout(data_loader) 
    bar_chart_section = create_bar_chart_layout(data_loader)  
    
    layout_children = [
        html.Div(className="dashboard-header", children=[
            html.H1("Loan Portfolio Dashboard", className="dashboard-title"),
        ]),
        
        html.Div(className="charts-grid", children=[
            html.Div(className="chart-card", children=[
                create_loan_chart_layout(data_loader) 
            ]),
            
            html.Div(className="chart-card", children=[
                create_second_chart_layout(data_loader) 
            ]),
        ]),
        
        html.Div(className="extra-section-row", children=[
            html.Div(className="chart-card full-width", children=[
                risk_subgrade_section 
            ])
        ]),
        
        html.Div(className="charts-grid-last", children=[
            html.Div(className="chart-card", children=[
                sunburst_section  
            ]),
            
            html.Div(className="chart-card", children=[
                bar_chart_section 
            ]),
        ]),
        
        dcc.Store(id='app-state', data={}),
        dcc.Interval(id='update-interval', interval=30000, n_intervals=0)
    ]
    
    return html.Div(className="dashboard-layout", children=layout_children)