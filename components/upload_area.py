from dash import html, dcc
import dash_mantine_components as dmc

def create_upload_area():
    """Create the file upload area component."""
    return dcc.Upload(
        id='upload-data',
        children=dmc.Paper([
            dmc.Group([
                dmc.Text(
                    "Drag and Drop or",
                    className="upload-text"
                ),
                dmc.Button(
                    "Select CSV File",
                    variant="outline",
                    className="upload-button"
                )
            ], position="center")
        ], className="upload-area"),
        multiple=False
    ) 