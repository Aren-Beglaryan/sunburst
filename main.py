import dash
from dash import dcc, html, Input, Output, State, ctx
import base64
import io
import pandas as pd
import plotly.express as px
import os
import shutil
from pathlib import Path

# Get the application root directory
APP_ROOT = Path(__file__).parent.absolute()

# Create uploads directory if it doesn't exist
UPLOADS_DIR = os.path.join(APP_ROOT, 'uploads')
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

LATEST_FILE = os.path.join(UPLOADS_DIR, 'latest.xlsx')

# Initialize the Dash app with proper configuration
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)

app.layout = html.Div([
    html.H1("Upload Excel File for Sunburst Chart"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Excel File')
        ]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-chart')
])

def parse_and_plot_df(df: pd.DataFrame) -> html.Div:
    if df.shape[1] < 4:
        return html.Div("Excel file must have at least 4 columns: Level1, Level2, Level3, Value")

    df.columns = ['Level1', 'Level2', 'Level3', 'Value']
    df = df.dropna(subset=['Level1', 'Level2', 'Level3', 'Value'])
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce').fillna(0)

    fig = px.sunburst(df, path=['Level1', 'Level2', 'Level3'], values='Value')
    return html.Div([dcc.Graph(figure=fig)])

def parse_and_plot(contents: str) -> html.Div:
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Save the uploaded file
        with open(LATEST_FILE, 'wb') as f:
            f.write(decoded)
            
        df = pd.read_excel(io.BytesIO(decoded))
        return parse_and_plot_df(df)
    except Exception as e:
        return html.Div([f"There was an error processing the file: {str(e)}"])

@app.callback(
    Output('output-chart', 'children'),
    Input('upload-data', 'contents')
)
def update_output(contents):
    if contents is not None:
        return parse_and_plot(contents)
    else:
        # Load the latest saved file if it exists
        if os.path.exists(LATEST_FILE):
            try:
                df = pd.read_excel(LATEST_FILE)
                return parse_and_plot_df(df)
            except Exception as e:
                return html.Div([f"Error loading latest file: {str(e)}"])
        return html.Div("Upload an Excel file to see the Sunburst chart.")

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8050))
    # Get host from environment variable or use default
    host = os.environ.get('HOST', '0.0.0.0')
    # Get debug mode from environment variable
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)
