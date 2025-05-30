from dash import html
import dash_mantine_components as dmc
from components import create_upload_area
from callbacks import update_output  # This imports the callback

def layout():
    """Home page layout."""
    return html.Div([
        dmc.Container([
            dmc.Stack([
                # Logo section
                html.Div([
                    html.Img(
                        src="https://via.placeholder.com/150x150.png?text=MyDeGiro",
                        className="mx-auto rounded-full shadow-lg border-2 border-secondary"
                    )
                ], className="mt-8"),
                
                # Title and description section
                html.Div([
                    html.H1(
                        "MyDeGiro Stocks",
                        className="text-heading-1 text-center text-secondary-lighter mb-4"
                    ),
                    html.P(
                        "Track and analyze your investment portfolio with ease. Upload your DeGiro export file to get started.",
                        className="text-body-lg text-center text-secondary"
                    )
                ], className="space-y-2"),
                
                # Upload section
                html.Div([
                    create_upload_area()
                ], className="w-full max-w-2xl mx-auto"),
                
                # Data display section
                html.Div(
                    id='output-data-upload',
                    className="bg-primary-light/50 rounded-lg p-6 shadow-xl"
                )
            ], spacing="xl", className="py-8")
        ], size="lg", className="px-4")
    ]) 