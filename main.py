import dash
from dash import dcc, html, Input, Output, State, ctx
import base64
import io
import pandas as pd
import plotly.express as px
import os

app = dash.Dash(__name__)

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
        # Load default Excel if no file uploaded
        default_path = 'example.xlsx'
        if os.path.exists(default_path):
            try:
                df = pd.read_excel(default_path)
                return parse_and_plot_df(df)
            except Exception as e:
                return html.Div([f"Error loading default file: {str(e)}"])
        return html.Div("Upload an Excel file to see the Sunburst chart.")

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=8050)
