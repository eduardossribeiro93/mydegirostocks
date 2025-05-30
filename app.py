import dash
from dash import html
from pages import home

# Initialize the Dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        "https://cdn.tailwindcss.com",  # Tailwind CSS CDN
    ],
    assets_folder='assets'  # This will automatically serve files from the assets folder
)

# Define the app layout with dark theme
app.layout = html.Div([
    # Add Tailwind configuration script
    html.Script("""
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: {
                            DEFAULT: '#0f172a',
                            light: '#1e293b',
                            lighter: '#334155',
                            dark: '#0a0f1a',
                        },
                        secondary: {
                            DEFAULT: '#64748b',
                            light: '#94a3b8',
                            lighter: '#cbd5e1',
                            dark: '#475569',
                        },
                        accent: {
                            DEFAULT: '#3b82f6',
                            light: '#60a5fa',
                            lighter: '#93c5fd',
                            dark: '#2563eb',
                        }
                    }
                }
            }
        }
    """),
    dash.page_container
], className="min-h-screen bg-primary text-secondary-lighter")

# Register pages
dash.register_page("home", path="/", layout=home.layout)

if __name__ == '__main__':
    app.run(debug=True) 