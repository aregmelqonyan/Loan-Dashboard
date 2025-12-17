from dash import Input, Output, State, callback
import plotly.graph_objects as go

def register_sunburst_callbacks(app, data_loader):

    @app.callback(
        Output('sunburst-chart', 'figure'),
        Output('sunburst-filter-state', 'data'),
        Input('sunburst-date-filter', 'start_date'),
        Input('sunburst-date-filter', 'end_date'),
        State('sunburst-filter-state', 'data')
    )
    def update_sunburst_chart(start_date, end_date, filter_state):
        if filter_state is None:
            filter_state = {}
        filter_state.update({
            'start_date': start_date,
            'end_date': end_date
        })
        fig = generate_sunburst_chart(start_date, end_date, data_loader)
        return fig, filter_state

    def generate_sunburst_chart(start_date, end_date, data_loader):
        try:
            sunburst_df = data_loader.get_sunburst_data(start_date, end_date)
            if sunburst_df.empty:
                return create_empty_figure("No Data", "No data for selected date range")
            grade_colors = {
                'A': '#1E88E5',
                'B': '#43A047',
                'C': '#FDD835',
                'D': '#FB8C00',
                'E': '#E53935',
                'F': '#8E24AA',
                'G': '#546E7A'
            }
            colors = []
            for _, row in sunburst_df.iterrows():
                parent_label = row['parent']
                label = row['label']
                if parent_label == "":
                    colors.append(grade_colors.get(label, '#1B5E20'))
                else:
                    parent_color = grade_colors.get(parent_label, '#1B5E20')
                    colors.append(parent_color)
            fig = go.Figure(go.Sunburst(
                ids=sunburst_df['id'],
                labels=sunburst_df['label'],
                parents=sunburst_df['parent'],
                values=sunburst_df['value'],
                branchvalues="total",
                marker=dict(colors=colors, line=dict(color='#111', width=1), colorscale=None),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Loan Amount: %{value:,.0f}<br>"
                    "<extra></extra>"
                ),
                customdata=sunburst_df['loan_count'],
                maxdepth=2
            ))
            fig.update_layout(
                title=dict(text="Loan Amount by Grade and Subgrade", font=dict(color="white", size=18),
                           y=0.97, x=0.5, xanchor="center"),
                margin=dict(l=0, r=0, t=60, b=0),
                paper_bgcolor='#0a0a0a',
                plot_bgcolor='#0a0a0a',
                height=500
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
