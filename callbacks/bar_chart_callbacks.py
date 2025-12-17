# callbacks/bar_chart_callbacks.py
from dash import Input, Output, State, callback
import plotly.graph_objects as go

def register_bar_chart_callbacks(app, data_loader):

    @app.callback(
        Output('bar-chart', 'figure'),
        Output('bar-filter-state', 'data'),
        Input('bar-variable-filter', 'value'),
        Input('bar-date-filter', 'start_date'),
        Input('bar-date-filter', 'end_date'),
        State('bar-filter-state', 'data')
    )
    def update_bar_chart(variable, start_date, end_date, filter_state):
        if filter_state is None:
            filter_state = {}
        filter_state.update({
            'variable': variable,
            'start_date': start_date,
            'end_date': end_date
        })
        fig = generate_bar_chart(variable, start_date, end_date, data_loader)
        return fig, filter_state

    def generate_bar_chart(variable, start_date, end_date, data_loader):
        try:
            grouped_data = data_loader.get_bar_chart_data(variable, start_date, end_date, top_n=30)
            if grouped_data.empty:
                return create_empty_figure("No Data", f"No data for {variable} or selected date range")
            grouped_data = grouped_data.drop_duplicates(subset=[variable], keep='first')
            if grouped_data.empty:
                return create_empty_figure("No Data", "No valid data after removing duplicates")
            grouped_data = grouped_data.sort_values('total_amount', ascending=True)
            y_values = grouped_data[variable].astype(str).tolist()
            x_values = grouped_data['loan_count'].tolist()
            count_values = grouped_data['loan_count'].tolist()
            min_length = min(len(y_values), len(x_values), len(count_values))
            y_values, x_values, count_values = y_values[:min_length], x_values[:min_length], count_values[:min_length]
            colors = '#4CAF50'
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=y_values,
                x=x_values,
                orientation='h',
                marker_color=colors,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Total Amount: $%{x:,.0f}<br>"
                    "<extra></extra>"
                ),
                customdata=grouped_data[['loan_count', 'avg_income', 'avg_int_rate']].values[:len(y_values)],
                text=[f"{count:,}" for count in count_values],
                textposition='outside',
                textfont=dict(color='white', size=12, family="Arial, sans-serif")
            ))
            variable_labels = {
                'purpose': 'Purpose',
                'home_ownership': 'Home Ownership',
                'emp_length': 'Employment Length'
            }
            title = f"Count by {variable_labels.get(variable, variable.title())}"
            fig.update_layout(
                title=dict(text=title, font=dict(color="white", size=18), y=0.97, x=0.5, xanchor="center"),
                xaxis=dict(tickfont=dict(color='#aaa'), gridcolor='#333', showgrid=True,
                           tickformat="~s", title_font=dict(color='white', size=14),
                           range=[0, max(x_values) * 1.15 if x_values else 0]),
                yaxis=dict(title=None, tickfont=dict(color='white', size=12),
                           automargin=True, categoryorder='array', categoryarray=y_values),
                plot_bgcolor='#0a0a0a',
                paper_bgcolor='#0a0a0a',
                margin=dict(l=10, r=80, t=80, b=50),
                height=500,
                showlegend=False,
                uniformtext=dict(minsize=10, mode='show')
            )
            return fig
        except Exception as e:
            return create_error_figure(f"Error: {str(e)[:100]}...")

    def create_empty_figure(title, message):
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=title, font=dict(color='white', size=16)),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            annotations=[dict(text=message, xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font=dict(size=14, color='#aaa'))],
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig

    def create_error_figure(error_message):
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Error", font=dict(color='white', size=16)),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            annotations=[dict(text=error_message, xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False, font=dict(size=12, color='#ff6b6b'))],
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig
