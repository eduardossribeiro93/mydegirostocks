from dash import dash_table

def create_data_table(df):
    """Create a styled data table from a pandas DataFrame."""
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df.columns],
        page_size=10,
        sort_action='native',
        filter_action='native',
        style_table={
            'overflowX': 'auto',
        },
        style_header={
            'backgroundColor': 'rgb(51, 65, 85)',  # primary-lighter
            'color': 'rgb(203, 213, 225)',  # secondary-lighter
            'fontWeight': '600',
            'padding': '16px',
            'textAlign': 'left'
        },
        style_data={
            'backgroundColor': 'rgb(30, 41, 59)',  # primary-light
            'color': 'rgb(148, 163, 184)',  # secondary-light
            'padding': '16px',
            'textAlign': 'left'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(51, 65, 85)',  # primary-lighter
            }
        ],
        style_cell={
            'minWidth': '100px',
            'maxWidth': '300px',
            'whiteSpace': 'normal',
        },
        style_filter={
            'backgroundColor': 'rgb(51, 65, 85)',  # primary-lighter
            'color': 'rgb(203, 213, 225)',  # secondary-lighter
        }
    ) 