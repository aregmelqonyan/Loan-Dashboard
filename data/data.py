import pandas as pd

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        self.df = pd.read_excel(self.file_path)
        if 'issue_date' in self.df.columns:
            self.df['issue_date'] = pd.to_datetime(self.df['issue_date'])
    
    def get_filtered_data(self, start_date=None, end_date=None, grades=None):
        df_filtered = self.df.copy()
        if start_date and end_date and 'issue_date' in df_filtered.columns:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df_filtered = df_filtered[
                (df_filtered['issue_date'] >= start_date) & 
                (df_filtered['issue_date'] <= end_date)
            ]
        if grades and 'grade' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['grade'].isin(grades)]
        return df_filtered
    
    def get_monthly_data(self, start_date=None, end_date=None, grades=None):
        df_filtered = self.get_filtered_data(start_date, end_date, grades)
        if df_filtered.empty:
            return pd.DataFrame()
        df_filtered['month'] = df_filtered['issue_date'].dt.to_period('M').dt.to_timestamp()
        monthly_data = df_filtered.groupby(['month', 'grade'])['loan_amount'].sum().reset_index()
        pivot_df = monthly_data.pivot(index='month', columns='grade', values='loan_amount')
        return pivot_df.fillna(0)
    
    def get_state_loan_data(self, start_date=None, end_date=None):
        df_filtered = self.get_filtered_data(start_date, end_date)
        if df_filtered.empty or 'address_state' not in df_filtered.columns:
            return pd.DataFrame()
        state_data = df_filtered.groupby('address_state').agg({
            'loan_amount': 'sum',
            'id': 'count',
            'annual_income': 'mean'
        }).reset_index()
        state_data.columns = ['state', 'total_loan_amount', 'loan_count', 'avg_income']
        if 'Good Or Bad Loan' in df_filtered.columns:
            df_filtered['Good Or Bad Loan'] = df_filtered['Good Or Bad Loan'].astype(str).str.strip()
            bad_loans_mask = df_filtered['Good Or Bad Loan'].str.contains('bad', case=False, na=False)
            bad_loans_df = df_filtered[bad_loans_mask]
            if len(bad_loans_df) > 0:
                bad_loans = bad_loans_df.groupby('address_state').agg({
                    'id': 'count',
                    'loan_amount': 'sum'
                }).reset_index()
                bad_loans.columns = ['state', 'bad_loan_count', 'bad_loan_amount']
                state_data = pd.merge(state_data, bad_loans, on='state', how='left')
            else:
                state_data['bad_loan_count'] = 0
                state_data['bad_loan_amount'] = 0.0
        else:
            state_data['bad_loan_count'] = 0
            state_data['bad_loan_amount'] = 0.0
        state_data['bad_loan_count'] = state_data['bad_loan_count'].fillna(0).astype(int)
        state_data['bad_loan_amount'] = state_data['bad_loan_amount'].fillna(0).astype(float)
        state_data['bad_loan_pct'] = state_data.apply(
            lambda row: (row['bad_loan_amount'] / row['total_loan_amount'] * 100) if row['total_loan_amount'] > 0 else 0,
            axis=1
        ).round(2)
        state_data['avg_income'] = state_data['avg_income'].round(0).astype(int)
        state_data['total_loan_amount'] = state_data['total_loan_amount'].astype(float)
        return state_data
    
    def get_risk_subgrade_data(self, start_date=None, end_date=None, grade=None):
        df_filtered = self.get_filtered_data(start_date, end_date)
        if df_filtered.empty:
            return pd.DataFrame()
        if 'sub_grade' in df_filtered.columns and 'grade' not in df_filtered.columns:
            df_filtered['grade'] = df_filtered['sub_grade'].str[0]
        if grade and 'grade' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['grade'] == grade]
        return df_filtered
    
    def get_bar_chart_data(self, variable, start_date=None, end_date=None, top_n=10):
        df_filtered = self.get_filtered_data(start_date, end_date)
        if df_filtered.empty or variable not in df_filtered.columns:
            return pd.DataFrame()
        df_filtered[variable] = df_filtered[variable].fillna('Unknown').astype(str).str.strip()
        grouped_data = df_filtered.groupby(variable).agg({
            'loan_amount': 'sum',
            'id': 'count',
            'annual_income': 'mean',
            'int_rate': 'mean'
        }).reset_index()
        grouped_data.columns = [variable, 'total_amount', 'loan_count', 'avg_income', 'avg_int_rate']
        grouped_data = grouped_data.sort_values('total_amount', ascending=False)
        if top_n < len(grouped_data):
            grouped_data = grouped_data.head(top_n)
        grouped_data = grouped_data.sort_values('total_amount', ascending=True)
        grouped_data['avg_income'] = grouped_data['avg_income'].round(0)
        grouped_data['avg_int_rate'] = grouped_data['avg_int_rate'].round(2)
        return grouped_data
    
    def get_sunburst_data(self, start_date=None, end_date=None):
        df_filtered = self.get_filtered_data(start_date, end_date)
        if df_filtered.empty:
            return pd.DataFrame()
        if 'sub_grade' not in df_filtered.columns or 'loan_amount' not in df_filtered.columns:
            return pd.DataFrame()
        if 'grade' not in df_filtered.columns and 'sub_grade' in df_filtered.columns:
            df_filtered['grade'] = df_filtered['sub_grade'].str[0]
        sunburst_data = []
        grade_data = df_filtered.groupby('grade').agg({'loan_amount': 'sum', 'id': 'count'}).reset_index()
        for _, row in grade_data.iterrows():
            sunburst_data.append({
                'id': row['grade'],
                'label': row['grade'],
                'parent': '',
                'value': row['loan_amount'],
                'loan_count': row['id']
            })
        subgrade_data = df_filtered.groupby(['grade', 'sub_grade']).agg({'loan_amount': 'sum', 'id': 'count'}).reset_index()
        for _, row in subgrade_data.iterrows():
            sunburst_data.append({
                'id': f"{row['grade']}-{row['sub_grade']}",
                'label': row['sub_grade'],
                'parent': row['grade'],
                'value': row['loan_amount'],
                'loan_count': row['id']
            })
        return pd.DataFrame(sunburst_data)
    
    def get_date_range(self):
        if self.df is not None and 'issue_date' in self.df.columns:
            return self.df['issue_date'].min(), self.df['issue_date'].max()
        return None, None
    
    def get_unique_grades(self):
        if self.df is not None and 'grade' in self.df.columns:
            return sorted(self.df['grade'].unique().tolist())
        return []
    
    def get_unique_values_for_variable(self, variable):
        if self.df is not None and variable in self.df.columns:
            values = self.df[variable].dropna().unique().tolist()
            return sorted([str(v).strip() for v in values])
        return []
