# loan_callbacks.py
from dash import Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def register_loan_callbacks(app, data_loader):
    """Register all loan chart related callbacks"""
    
    @app.callback(
        Output('loan-chart', 'figure'),
        Output('loan-filter-state', 'data'),
        Input('loan-grade-filter', 'value'),
        Input('loan-date-filter', 'start_date'),
        Input('loan-date-filter', 'end_date'),
        State('loan-filter-state', 'data')
    )
    def update_loan_chart_dynamically(selected_grades, start_date, end_date, filter_state):
        """Update loan chart dynamically when filters change"""
        
        if selected_grades is None:
            all_grades = data_loader.get_unique_grades()
            selected_grades = [g for g in all_grades if g in ['A', 'B', 'C', 'D', 'E']]
        
        if filter_state is None:
            filter_state = {}
        
        filter_state.update({
            'grades': selected_grades or [],
            'start_date': start_date,
            'end_date': end_date
        })
        
        fig = generate_loan_chart(selected_grades, start_date, end_date, data_loader)
        
        return fig, filter_state
    
    def generate_loan_chart(selected_grades, start_date, end_date, data_loader):
        """Generate loan chart with given filters"""
        
        if not selected_grades:
            return create_empty_figure("No grades selected", "Please select at least one grade")
        
        try:
            pivot_df = data_loader.get_monthly_data(start_date, end_date, selected_grades)
            
            if pivot_df.empty:
                return create_empty_figure("No data for selected filters", 
                                         "Adjust filters or try different dates/grades")
            
            fig = go.Figure()
            
            colors = {
                'A': '#1B5E20',  
                'B': '#4CAF50',  
                'C': '#FBC02D', 
                'D': '#FB8C00',
                'E': '#E53935',
                'F': '#8E24AA',
                'G': '#546E7A', 
            }
            
            for grade in selected_grades:
                if grade in pivot_df.columns:
                    fig.add_trace(go.Scatter(
                        x=pivot_df.index,
                        y=pivot_df[grade],
                        mode='lines+markers',
                        name=f'Grade {grade}',
                        line=dict(color=colors.get(grade, '#636efa'), width=2.5),
                        marker=dict(size=8, symbol='circle'),
                       hovertemplate=(
                            f"<b>Grade {grade}</b><br>"
                            "Month: %{x|%Y-%m}<br>"
                            "Loan Amount: %{y:,.0f}<br>"
                            "<extra></extra>"
                        )
                    ))
            fig.update_layout(
                title=dict(
                    text="Monthly Loan Amount by Grade",
                    font=dict(color="white", size=18),
                    y=0.94,
                    x=0.5,
                    xanchor="center",
                ),
                xaxis=dict(
                    showgrid=False,
                    tickformat="%Y-%m", 
                    tickfont=dict(color='#aaa'),
                ),
                yaxis=dict(
                    gridcolor='gray',
                    tickfont=dict(color="white"), 
                ),
                hovermode='closest',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',

                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=0.93,           
                    xanchor="center", 
                    x=0.5,            
                    font=dict(color="white"),
                    bgcolor='rgba(0,0,0,0)'  
                ),
                height=500
            )
                        
            return fig
            
        except Exception as e:
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
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
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
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
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