from dash import Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def register_map_callbacks(app, data_loader):
    """Register all map chart related callbacks"""
    
    @app.callback(
        Output('second-chart', 'figure'),
        Output('second-filter-state', 'data'),
        Input('second-date-filter', 'start_date'),
        Input('second-date-filter', 'end_date'),
        State('second-filter-state', 'data')
    )
    def update_second_chart_dynamically(start_date, end_date, filter_state):
        """Update US map dynamically when date filter changes"""
        
        if filter_state is None:
            filter_state = {}
        
        filter_state.update({
            'start_date': start_date,
            'end_date': end_date
        })
        
        fig = generate_us_map(start_date, end_date, data_loader)
        
        return fig, filter_state
    
    def generate_us_map(start_date, end_date, data_loader):
        """Generate US choropleth map for state loan distribution"""
        
        try:
            state_data = data_loader.get_state_loan_data(start_date, end_date)
            
            if state_data.empty:
                return create_empty_figure("No Data", 
                                        "No data for selected date")
            
            hover_texts = []
            for _, row in state_data.iterrows():
                hover_text = (
                    f"State: {row['state']}<br>"
                    f"Total Loans: {row['loan_count']:,}<br>"
                    f"Total Amount: ${row['total_loan_amount']:,.0f}<br>"
                    f"Bad Loans: {row['bad_loan_count']:,}<br>"
                    f"Bad Amount: ${row['bad_loan_amount']:,.0f}<br>"
                    f"Bad Loan %: {row['bad_loan_pct']:.2f}%<br>"
                    f"Avg Income: ${row['avg_income']:,.0f}"
                )
                hover_texts.append(hover_text)
            
            fig = go.Figure(data=go.Choropleth(
                locations=state_data['state'],
                z=state_data['total_loan_amount'].astype(float),
                locationmode='USA-states',
                colorscale=[
                    [0.0, '#E8F5E9'],
                    [0.2, '#C8E6C9'],
                    [0.4, '#A5D6A7'],
                    [0.6, '#81C784'],
                    [0.8, '#66BB6A'],
                    [1.0, '#1B5E20']
                ],
                zmin=state_data['total_loan_amount'].min(),
                zmax=state_data['total_loan_amount'].max(),
                marker_line_color='white',
                marker_line_width=0.5,
                hoverinfo='location+z+text',
                hovertext=hover_texts,
                hovertemplate="%{hovertext}<extra></extra>",
                hoverlabel=dict(
                font=dict(color='white'),
                bgcolor='#111'
                    ),
                    colorbar=dict(
                        title=dict(text="Loan Amount", font=dict(color='white')),
                        tickfont=dict(color='white')
                    )
                ))
            
            fig.update_layout(
                title=dict(
                    text="Loan Portfolio Map",
                    font=dict(color="white", size=20),
                    y=0.95,
                    x=0.5,
                    xanchor="center",
                ),
                geo=dict(
                    scope='usa',
                    projection=go.layout.geo.Projection(type='albers usa'),
                    showlakes=True,
                    lakecolor='rgb(85, 173, 240)',
                    bgcolor='rgba(0,0,0,0)',
                    landcolor='#222',
                    subunitcolor='grey',
                    showland=True,
                    showcoastlines=True,
                    coastlinecolor='grey',
                    coastlinewidth=0.5,
                    subunitwidth=0.5
                ),
                paper_bgcolor='#111',
                plot_bgcolor='#1a1a1a',
                margin=dict(l=0, r=0, t=80, b=0),
                height=500,
                coloraxis_colorbar=dict(
                    title_font=dict(color='white', size=12),
                    tickfont=dict(color='white', size=11),
                    thickness=15,
                    len=0.8
                )
            )
            
            return fig
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return create_error_figure(f"Error: {str(e)[:100]}...")
    
    def create_empty_figure(title, message):
        """Create an empty figure with a message"""
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='white', size=16)
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#111',
            annotations=[dict(
                text=message,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color='#aaa')
            )],
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig
    
    def create_error_figure(error_message):
        """Create an error figure"""
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text="Error",
                font=dict(color='white', size=16)
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#111',
            annotations=[dict(
                text=error_message,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color='#ff6b6b')
            )],
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig