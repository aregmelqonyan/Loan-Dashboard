from dash import Input, Output, State, callback, no_update
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash import html

def register_risk_subgrade_callbacks(app, data_loader):
    """Register callbacks for risk subgrade analysis"""
    
    @app.callback(
        Output('summary-data-store', 'data'),
        Input('risk-date-filter', 'start_date'),
        Input('risk-date-filter', 'end_date'),
        Input('risk-grade-filter', 'value')
    )
    def update_summary_cards(start_date, end_date, selected_grade):
        """Update summary cards with grade amounts"""
        try:
            df_filtered = data_loader.get_filtered_data(start_date, end_date)
            
            if df_filtered.empty:
                return [], {}
            
            if 'grade' not in df_filtered.columns and 'sub_grade' in df_filtered.columns:
                df_filtered['grade'] = df_filtered['sub_grade'].str[0]
            
            grade_summary = df_filtered.groupby('grade').agg({
                'loan_amount': 'sum',
            }).reset_index()
            
            grade_summary.columns = ['grade', 'total_amount']
            
            grade_summary = grade_summary.sort_values('grade')
            
            cards = []
            summary_data = {}
            
            for _, row in grade_summary.iterrows():
                grade = row['grade']
                amount = row['total_amount']
                
                summary_data[grade] = {
                    'amount': amount,
                }
                
                formatted_amount = f"${amount:,.0f}"
                
                card_class = "summary-card"
                if selected_grade and grade == selected_grade:
                    card_class += " active"
                
                card = html.Div(
                    className=card_class,
                    children=[
                        html.Div(f"Grade {grade}", className="grade-label"),
                        html.Div(formatted_amount, className="amount-value"),
                    ]
                )
                cards.append(card)
            
            return cards, summary_data
            
        except Exception as e:
            return [], {}
    
    @app.callback(
        Output('risk-grade-filter', 'disabled'),
        Input('risk-group-toggle', 'on')
    )
    def toggle_dropdown(toggle_on):
        """Enable/disable grade dropdown based on toggle"""
        return not toggle_on
    
    @app.callback(
        Output('risk-grade-filter', 'value'),
        Input('risk-group-toggle', 'on')
    )
    def clear_dropdown(toggle_on):
        """Clear dropdown value when toggle is turned off"""
        if not toggle_on:
            return None
        return no_update
    
    @app.callback(
        Output('risk-subgrade-chart', 'figure'),
        Output('risk-filter-state', 'data'),
        Input('risk-date-filter', 'start_date'),
        Input('risk-date-filter', 'end_date'),
        Input('risk-group-toggle', 'on'),
        Input('risk-grade-filter', 'value'),
        State('risk-filter-state', 'data')
    )
    def update_risk_chart_dynamically(start_date, end_date, toggle_on, selected_grade, filter_state):
        """Update risk subgrade chart dynamically when filters change"""
        
        if filter_state is None:
            filter_state = {}
        
        filter_state.update({
            'start_date': start_date,
            'end_date': end_date,
            'toggle_on': toggle_on,
            'selected_grade': selected_grade if toggle_on else None
        })
        
        fig = generate_risk_subgrade_chart(start_date, end_date, toggle_on, selected_grade, data_loader)
        
        return fig, filter_state
    
    def generate_risk_subgrade_chart(start_date, end_date, toggle_on, selected_grade, data_loader):
        """Generate chart for risk subgrade analysis with green colors"""
        
        try:
            df_filtered = data_loader.get_filtered_data(start_date, end_date)
            
            if df_filtered.empty:
                return create_empty_figure("No Data", "No data for selected date range")
            
            if 'sub_grade' not in df_filtered.columns:
                return create_empty_figure("Missing Data", "Subgrade column not found in dataset")
            
            df_filtered['grade'] = df_filtered['sub_grade'].str[0]
            
            if toggle_on and selected_grade:
                df_filtered = df_filtered[df_filtered['grade'] == selected_grade]
                
                if df_filtered.empty:
                    return create_empty_figure("No Data", f"No data for grade {selected_grade}")
                
                grouped_data = df_filtered.groupby('sub_grade').agg({
                    'loan_amount': ['sum', 'count'],
                    'annual_income': 'mean',
                    'int_rate': 'mean'
                }).reset_index()
                
                grouped_data.columns = ['sub_grade', 'total_amount', 'loan_count', 'avg_income', 'avg_int_rate']
                
                grouped_data['sort_key'] = grouped_data['sub_grade'].str[0] + grouped_data['sub_grade'].str[1:].str.pad(2, 'left', '0')
                grouped_data = grouped_data.sort_values('sort_key')
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=grouped_data['sub_grade'],
                    y=grouped_data['total_amount'],
                    name='Total Amount',
                    marker_color='#388E3C',
                    text=[f"{v:,.0f}" for v in grouped_data['total_amount']],
                    textposition='outside',                                   
                    textfont=dict(color='white', size=12),
                    hovertemplate=(
                        "%{x}<br>"
                        "Loan Amount: %{y:,.0f}<br>"
                        "<extra></extra>"
                    ),
                    customdata=grouped_data[['loan_count', 'avg_income', 'avg_int_rate']].values
                ))
                
                fig.update_layout(
                    title=dict(
                        text=f"Loan Amount by Subgrade ({selected_grade})",
                        font=dict(color="white", size=16),
                        y=0.95,
                        x=0.5,
                        xanchor="center",
                    ),
                    xaxis=dict(
                        tickfont=dict(color='#aaa'),
                        gridcolor='#333',
                        showgrid=False
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white'),
                        gridcolor='#333',
                        title_font=dict(color='white'),
                        showgrid=True,
                        gridwidth=0.5
                    ),
                    hovermode='closest',
                    hoverlabel=dict(
                        bgcolor="green",
                        font=dict(color="white"),
                        bordercolor="green"
                    ),
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    showlegend=False,
                    margin=dict(l=50, r=50, t=60, b=50),
                    height=400
                )
                
            else:
                grouped_data = df_filtered.groupby('grade').agg({
                    'loan_amount': ['sum', 'count'],
                    'annual_income': 'mean',
                    'int_rate': 'mean',
                    'sub_grade': lambda x: len(x.unique())  
                }).reset_index()
                
                grouped_data.columns = ['grade', 'total_amount', 'loan_count', 'avg_income', 'avg_int_rate', 'subgrade_count']
                
                grouped_data = grouped_data.sort_values('grade')
                
                fig = go.Figure()
                
                for grade in grouped_data['grade']:
                    grade_data = grouped_data[grouped_data['grade'] == grade]
                    color = '#388E3C'
                    
                    fig.add_trace(go.Bar(
                        x=[grade],
                        y=grade_data['total_amount'],
                        name=f'Grade {grade}',
                        marker_color=color,
                        text=[f"{grade_data['total_amount'].values[0]:,.0f}"],
                        textposition='outside',
                        textfont=dict(color='white', size=12),
                        hovertemplate=(
                            "Grade %{x}<br>"
                            "Loan Amount: %{y:,.0f}<br>"
                            "<extra></extra>"
                        ),
                        customdata=grade_data[['loan_count', 'avg_income', 'avg_int_rate', 'subgrade_count']].values
                    ))
                
                fig.update_layout(
                    title=dict(
                        text="Loan Amount by Grade",
                        font=dict(color="white", size=16),
                        y=0.95,
                        x=0.5,
                        xanchor="center",
                    ),
                    xaxis=dict(
                        tickfont=dict(color='#aaa'),
                        gridcolor='#333',
                        showgrid=False
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white'),
                        gridcolor='#333',
                        title_font=dict(color='white'),
                        showgrid=True,
                        gridwidth=0.5
                    ),
                    hovermode='closest',
                    hoverlabel=dict(
                        bgcolor="green",
                        font=dict(color="white"),
                        bordercolor="green"
                    ),
                    plot_bgcolor='#1a1a1a',
                    paper_bgcolor='#1a1a1a',
                    bargap=0.3,
                    bargroupgap=0.1,
                    showlegend=False,
                    margin=dict(l=50, r=50, t=60, b=50),
                    height=400
                )
            
            return fig
            
        except Exception as e:
            return create_error_figure(f"Error: {str(e)[:100]}...")
    
    def create_empty_figure(message, subtitle=""):
        """Create an empty figure with a message"""
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text=message,
                font=dict(color='white', size=14)
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            annotations=[dict(
                text=subtitle if subtitle else "Adjust filters to view data",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color='#aaa')
            )],
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig
    
    def create_error_figure(error_message):
        """Create an error figure"""
        fig = go.Figure()
        fig.update_layout(
            title=dict(
                text="Error",
                font=dict(color='white', size=14)
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            annotations=[dict(
                text=error_message,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color='#ff6b6b')
            )],
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig