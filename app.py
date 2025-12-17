import dash
from dash import Dash
import dash_bootstrap_components as dbc
import os
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data.data import DataLoader
from layouts import dashboard_layout
from layouts.risk_subgrade_layout import create_risk_subgrade_layout
from callbacks.loan_callbacks import register_loan_callbacks
from callbacks.map_callbacks import register_map_callbacks
from callbacks.risk_subgrade_callbacks import register_risk_subgrade_callbacks
from utils.load_css import load_css_files, setup_assets_directory

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

app.title = "Loan Analytics Dashboard"
server = app.server

css_files, index_string = load_css_files()
app.index_string = index_string

def initialize_app():
    DATA_PATH = "portfolio.xlsx"
    
    if os.path.exists(DATA_PATH):
        data_loader = DataLoader(DATA_PATH)
    else:
        data_loader = None
    
    app.layout = dashboard_layout.create_dashboard_layout(data_loader)
    
    if data_loader:
        register_loan_callbacks(app, data_loader)
        register_map_callbacks(app, data_loader)
        register_risk_subgrade_callbacks(app, data_loader)
        from callbacks.sunburst_callbacks import register_sunburst_callbacks
        register_sunburst_callbacks(app, data_loader)
        from callbacks.bar_chart_callbacks import register_bar_chart_callbacks
        register_bar_chart_callbacks(app, data_loader)
    else:
        register_sample_callbacks(app)
    
    return app

def register_sample_callbacks(app):
    @app.callback(
        dash.Output('loan-chart', 'figure'),
        dash.Output('loan-filter-state', 'data'),
        dash.Input('loan-grade-filter', 'value'),
        dash.Input('loan-date-filter', 'start_date'),
        dash.Input('loan-date-filter', 'end_date'),
        dash.State('loan-filter-state', 'data')
    )
    def sample_loan_callback(selected_grades, start_date, end_date, filter_state):
        if filter_state is None:
            filter_state = {}
        
        filter_state.update({
            'grades': selected_grades or ['A', 'B', 'C'],
            'start_date': start_date,
            'end_date': end_date
        })
        
        if not selected_grades:
            selected_grades = ['A', 'B', 'C']
        
        dates = pd.date_range(start='2023-01-01', end='2023-12-01', freq='MS')
        fig = go.Figure()
        
        colors = {
            'A': '#1B5E20',  
            'B': '#4CAF50',  
            'C': '#FBC02D', 
            'D': '#FB8C00',
            'E': '#E53935',
        }
        
        for grade in selected_grades:
            if grade in colors:
                amounts = np.random.randint(100000, 1000000, size=len(dates))
                amounts = amounts.cumsum()
                
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=amounts,
                    mode='lines+markers',
                    name=f'Grade {grade}',
                    line=dict(color=colors.get(grade, '#636efa'), width=2.5),
                    marker=dict(size=8, symbol='circle'),
                    hovertemplate=(
                        f"<b>Grade {grade}</b><br>"
                        "Date: %{x|%b %Y}<br>"
                        "Amount: $%{y:,.0f}<br>"
                        "<extra></extra>"
                    )
                ))
        
        fig.update_layout(
            title=dict(text="Sample Loan Chart (No Data File)", font=dict(color="white", size=18), y=0.97, x=0.5, xanchor="center"),
            xaxis=dict(showgrid=False, tickformat="%Y-%m", tickfont=dict(color='#aaa')),
            yaxis=dict(gridcolor='gray', tickfont=dict(color="white")),
            hovermode='x unified',
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#111',
            legend=dict(orientation="h", y=1.02, xanchor="right", x=1, font=dict(color="white")),
            margin=dict(l=50, r=50, t=90, b=50),
            height=500
        )
        
        return fig, filter_state
    
    @app.callback(
        dash.Output('risk-subgrade-chart', 'figure'),
        dash.Output('risk-filter-state', 'data'),
        dash.Output('summary-data-store', 'data'),
        dash.Input('risk-date-filter', 'start_date'),
        dash.Input('risk-date-filter', 'end_date'),
        dash.Input('risk-group-toggle', 'on'),
        dash.Input('risk-grade-filter', 'value'),
        dash.State('risk-filter-state', 'data')
    )
    def sample_risk_callback(start_date, end_date, toggle_on, selected_grade, filter_state):
        if filter_state is None:
            filter_state = {}
        
        filter_state.update({
            'start_date': start_date,
            'end_date': end_date,
            'toggle_on': toggle_on,
            'selected_grade': selected_grade
        })
        
        grades = ['A', 'B', 'C', 'D', 'E', 'F']
        amounts = [130694075, 87442450, 63920800, 44165100, 18910450, 6348075]
        counts = [12500, 8900, 6500, 4200, 1800, 600]
        cards = []
        summary_data = {}
        
        for grade, amount, count in zip(grades, amounts, counts):
            summary_data[grade] = {'amount': amount, 'count': count}
            card = dash.html.Div(className="summary-card", children=[
                dash.html.Div(f"Grade {grade}", className="grade-label"),
                dash.html.Div(f"${amount:,}", className="amount-value"),
                dash.html.Div(f"{count:,} loans", className="count-value")
            ])
            cards.append(card)
        
        if toggle_on and selected_grade:
            subgrades = [f'{selected_grade}{i}' for i in range(1, 6)]
            amounts = np.random.randint(1000000, 5000000, size=5)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=subgrades, y=amounts, marker_color=['#1B5E20', '#2E7D32', '#388E3C', '#43A047', '#4CAF50']))
            fig.update_layout(title=f"Sample Subgrade Analysis for Grade {selected_grade}", plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', font_color='white')
        else:
            fig = go.Figure()
            for grade, amount in zip(grades, amounts):
                fig.add_trace(go.Bar(
                    x=[grade],
                    y=[amount],
                    name=f'Grade {grade}',
                    marker_color={
                        'A': '#1B5E20', 'B': '#2E7D32', 'C': '#388E3C',
                        'D': '#43A047', 'E': '#4CAF50', 'F': '#66BB6A'
                    }.get(grade, '#81C784')
                ))
            fig.update_layout(title="Sample Loan Distribution by Risk Grade", plot_bgcolor='#1a1a1a', paper_bgcolor='#1a1a1a', font_color='white', showlegend=False, bargap=0.3)
        
        return fig, filter_state, cards, summary_data
    
    @app.callback(
        dash.Output('second-chart', 'figure'),
        dash.Output('second-filter-state', 'data'),
        dash.Input('second-date-filter', 'start_date'),
        dash.Input('second-date-filter', 'end_date'),
        dash.State('second-filter-state', 'data')
    )
    def sample_map_callback(start_date, end_date, filter_state):
        if filter_state is None:
            filter_state = {}
        
        filter_state.update({'start_date': start_date, 'end_date': end_date})
        
        states = ['CA', 'TX', 'NY', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        state_names = {'CA':'California','TX':'Texas','NY':'New York','FL':'Florida','IL':'Illinois','PA':'Pennsylvania','OH':'Ohio','GA':'Georgia','NC':'North Carolina','MI':'Michigan'}
        data = []
        for state in states:
            data.append({
                'state': state,
                'total_loan_amount': np.random.randint(1000000, 10000000),
                'loan_count': np.random.randint(1000, 10000),
                'bad_loan_count': np.random.randint(50, 500),
                'bad_loan_pct': np.random.uniform(1.0, 8.0),
                'avg_income': np.random.randint(50000, 90000)
            })
        state_df = pd.DataFrame(data)
        state_df['bad_loan_pct'] = state_df['bad_loan_pct'].round(1)
        
        fig = go.Figure(data=go.Choropleth(
            locations=state_df['state'],
            z=state_df['total_loan_amount'].astype(float),
            locationmode='USA-states',
            colorscale=[[0.0,'#E8F5E9'],[0.2,'#C8E6C9'],[0.4,'#A5D6A7'],[0.6,'#81C784'],[0.8,'#66BB6A'],[1.0,'#1B5E20']],
            colorbar_title="Loan Amount ($)",
            zmin=state_df['total_loan_amount'].min(),
            zmax=state_df['total_loan_amount'].max(),
            marker_line_color='white',
            marker_line_width=0.5,
            hoverinfo='location+z+text',
            hovertext=state_df.apply(lambda row: (
                f"<b>{state_names.get(row['state'], row['state'])}</b><br>"
                f"Total Loans: {row['loan_count']:,}<br>"
                f"Total Amount: ${row['total_loan_amount']:,.0f}<br>"
                f"Bad Loans: {row['bad_loan_count']:,}<br>"
                f"Bad Loan %: {row['bad_loan_pct']:.1f}%<br>"
                f"Avg Income: ${row['avg_income']:,.0f}"
            ), axis=1),
            hovertemplate="%{hovertext}<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(text="Sample Map (No Data File)", font=dict(color="white", size=20), y=0.95, x=0.5, xanchor="center"),
            geo=dict(scope='usa', projection=go.layout.geo.Projection(type='albers usa'), showlakes=True, lakecolor='rgb(85, 173, 240)', bgcolor='rgba(0,0,0,0)', landcolor='#222', subunitcolor='grey', showland=True, showcoastlines=True, coastlinecolor='grey', coastlinewidth=0.5, subunitwidth=0.5),
            paper_bgcolor='#111',
            plot_bgcolor='#1a1a1a',
            margin=dict(l=0, r=0, t=80, b=0),
            height=500,
            coloraxis_colorbar=dict(title_font=dict(color='white', size=12), tickfont=dict(color='white', size=11), thickness=15, len=0.8)
        )
        
        return fig, filter_state

if __name__ == '__main__':
    setup_assets_directory()
    app = initialize_app()
    app.run(debug=True, host='0.0.0.0', port=8080)
