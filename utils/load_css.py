import os
import shutil

def load_css_files():
    """Load all CSS files for the modular layout"""
    css_files = [
        'assets/css/ml_amount_bg.css',
        'assets/css/second.css',
        'assets/css/dashboard_layout.css',
        'assets/css/risk_subgrade_layout.css',
        'assets/css/bar_chart_layout.css',
        'assets/css/sunburst_callbacks.css ',
    ]

    string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>Loan Analytics Dashboard</title>
            {%favicon%}
            {%css%}
            <!-- Load all CSS files -->
            <link rel="stylesheet" href="assets/css/ml_amount_bg.css">
            <link rel="stylesheet" href="assets/css/second.css">
            <link rel="stylesheet" href="assets/css/dashboard_layout.css">
            <link rel="stylesheet" href="assets/css/risk_subgrade_layout.css">
            <link rel="stylesheet" href="assets/css/bar_chart_layout.css">
            <link rel="stylesheet" href="assets/css/sunburst_callbacks.css">
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

    return css_files, string

def setup_assets_directory():
    """Create the necessary directory structure for CSS files"""
    
    assets_dir = 'assets'
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    css_dirs = ['css']
    
    for css_dir in css_dirs:
        full_path = os.path.join(assets_dir, css_dir)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
  
    callbacks_dir = 'callbacks'
    if not os.path.exists(callbacks_dir):
        os.makedirs(callbacks_dir)
