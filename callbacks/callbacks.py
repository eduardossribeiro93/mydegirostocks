import base64
import io
from dash import html, Input, Output, State, callback
import pandas as pd
from components import create_data_table

@callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    """Callback to handle file upload and display data."""
    if contents is None:
        return None
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            data_table = create_data_table(df)
            
            return html.Div([
                html.Div([
                    html.H2(
                        f"File: {filename}",
                        className="text-heading-2 text-secondary-lighter"
                    ),
                    html.H3(
                        "Data Preview:",
                        className="text-heading-3 text-secondary mt-2"
                    ),
                ], className="border-b border-secondary-dark pb-4"),
                html.Div([
                    data_table
                ], className="data-table-container")
            ], className="space-y-4")
        else:
            return html.Div(
                'Please upload a CSV file.',
                className="error-message"
            )
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return html.Div([
            html.H2(
                'Error Processing File',
                className="text-heading-2 text-red-400"
            ),
            html.P(
                f'An error occurred while processing {filename}:',
                className="text-body text-secondary mt-2"
            ),
            html.Pre(
                str(e),
                className="bg-primary-light text-secondary p-4 rounded-lg font-mono text-body-sm mt-2"
            )
        ], className="space-y-2") 