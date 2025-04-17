import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import io
import base64
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the Excel file (default data)
default_file_path = 'example.xlsx'  # Change this to the correct path if needed
df = pd.read_excel(default_file_path, sheet_name='Sheet1')

# Rename the columns for easier access
df.columns = ['MainClass', 'SubClass', 'SubSubClass', 'Value']

# Create the hierarchical structure for the Sunburst Chart
df['ID'] = df['MainClass'] + " - " + df['SubClass'] + " - " + df['SubSubClass']
df['Parent'] = df['MainClass'] + " - " + df['SubClass']

# Prepare the sunburst chart data
def prepare_sunburst(df):
    sunburst_data = {
        'ids': df['ID'].tolist(),
        'labels': df['SubSubClass'].tolist(),
        'parents': df['Parent'].tolist(),
        'values': df['Value'].tolist()
    }
    return pd.DataFrame(sunburst_data)

sunburst_df = prepare_sunburst(df)

def get_default_excel():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Sunburst Chart", style={'textAlign': 'center', 'marginTop': '30px'}),
    html.P("This app allows you to upload and visualize hierarchical data as a Sunburst chart.", style={'textAlign': 'center'}),

    html.Div([
        html.H3("1. Upload Excel File"),
        dcc.Upload(
            id='upload-data',
            children=html.Button('Upload Your Excel File'),
            multiple=False,
            style={
                'padding': '10px 20px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
            }
        ),
        html.P("Upload an Excel file with 'MainClass', 'SubClass', 'SubSubClass', and 'Value' columns.", style={'fontStyle': 'italic', 'color': '#555'})
    ], style={'width': '40%', 'margin': '0 auto', 'textAlign': 'center'}),

    html.Div([
        html.H3("2. Generate Sunburst Plot"),
        html.Button('Make Plot', id='make-plot', n_clicks=0, style={
            'padding': '10px 20px',
            'backgroundColor': '#28a745',
            'color': 'white',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer',
        }),
        html.P("Click to generate a Sunburst chart from the uploaded data.", style={'fontStyle': 'italic', 'color': '#555'})
    ], style={'width': '40%', 'margin': '20px auto', 'textAlign': 'center'}),

    html.Div([
        html.H3("3. Download Default Data"),
        html.A('Download Default Data (Excel)', id='download-link', href='', download="default_data.xlsx", target="_blank",
               style={
                   'padding': '10px 20px',
                   'backgroundColor': '#ffc107',
                   'color': 'black',
                   'border': 'none',
                   'borderRadius': '5px',
                   'textDecoration': 'none',
                   'cursor': 'pointer'
               }),
        html.P("Download the default dataset to modify it and upload it again.", style={'fontStyle': 'italic', 'color': '#555'})
    ], style={'width': '40%', 'margin': '20px auto', 'textAlign': 'center'}),

    dcc.Graph(id='sunburst-chart', style={'marginTop': '20px'})
])

# Handle uploaded Excel file
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_excel(io.BytesIO(decoded))
        df.columns = ['MainClass', 'SubClass', 'SubSubClass', 'Value']
        df['ID'] = df['MainClass'] + " - " + df['SubClass'] + " - " + df['SubSubClass']
        df['Parent'] = df['MainClass'] + " - " + df['SubClass']
        return prepare_sunburst(df)
    except Exception as e:
        print(e)
        return None

# Callback to update chart
@app.callback(
    [Output('sunburst-chart', 'figure'),
     Output('download-link', 'href')],
    [Input('make-plot', 'n_clicks')],
    [Input('upload-data', 'contents')]
)
def update_chart(n_clicks, contents):
    if n_clicks > 0 and contents:
        df_uploaded = parse_contents(contents)
        if df_uploaded is not None:
            fig = go.Figure(go.Sunburst(
                ids=df_uploaded['ids'],
                labels=df_uploaded['labels'],
                parents=df_uploaded['parents'],
                values=df_uploaded['values'],
                maxdepth=4,
                insidetextorientation='radial'
            ))
            fig.update_layout(title="Sunburst Chart Example", margin=dict(t=10, l=10, r=10, b=10))
            return fig, ''

    # Show default chart if nothing uploaded
    fig = go.Figure(go.Sunburst(
        ids=sunburst_df['ids'],
        labels=sunburst_df['labels'],
        parents=sunburst_df['parents'],
        values=sunburst_df['values'],
        maxdepth=4,
        insidetextorientation='radial'
    ))
    fig.update_layout(title="Sunburst Chart Example", margin=dict(t=10, l=10, r=10, b=10))
    excel_buffer = get_default_excel()
    excel_data = base64.b64encode(excel_buffer.read()).decode()
    return fig, f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_data}'

if __name__ == '__main__':
    app.run(debug=True)