# MyDeGiro Stocks

A Dash application to track investments and historical performance from DeGiro exports.

## Features (to-do)

- Multi-period chart
- Monthly/weekly performance
- Historical performance metrics
- Current portfolio characteristics
- Multi-benchmark comparison

## Requirements

- Python 3.9 or higher
- Poetry for dependency management

## Installation

1. Clone this repository
2. Install dependencies using Poetry:
```bash
poetry install
```

## Running the Application

1. Activate the Poetry environment:
```bash
poetry shell
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://127.0.0.1:8050`

## Usage

1. Launch the application
2. Use the drag-and-drop interface or click to select a CSV file
3. The application will display the first 10 rows of your data in a table format

## Development

This project uses Poetry for dependency management. To add new dependencies:

```bash
poetry add package-name
```
