#!/usr/bin/env python3
"""
Extract cells tagged with 'caption' and 'chart' from a Jupyter notebook
and generate a static HTML file with captions and charts side-by-side.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import markdown


def load_notebook(notebook_path: str) -> Dict[str, Any]:
    """Load a Jupyter notebook file as JSON."""
    with open(notebook_path, 'r') as f:
        return json.load(f)


def extract_tagged_cells(notebook: Dict[str, Any]) -> tuple[List[Dict], List[Dict]]:
    """
    Extract cells with specific tags from the notebook.

    Returns:
        tuple: (caption_cells, chart_cells)
    """
    caption_cells = []
    chart_cells = []

    for cell in notebook.get('cells', []):
        tags = cell.get('metadata', {}).get('tags', [])

        if 'caption' in tags and cell.get('cell_type') == 'markdown':
            caption_cells.append(cell)
        elif 'chart' in tags and cell.get('cell_type') == 'code':
            chart_cells.append(cell)

    return caption_cells, chart_cells


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to HTML using the markdown library.
    Supports full markdown syntax including headers, lists, code blocks, etc.
    """
    # Configure markdown with useful extensions
    md = markdown.Markdown(extensions=[
        'extra',        # Adds support for tables, fenced code blocks, etc.
        'nl2br',        # Converts newlines to <br> tags
        'sane_lists',   # Better list handling
    ])

    return md.convert(markdown_text)


def extract_image_from_cell(cell: Dict[str, Any]) -> str:
    """Extract base64 image data from a code cell output."""
    outputs = cell.get('outputs', [])

    for output in outputs:
        data = output.get('data', {})
        if 'image/png' in data:
            # PNG images are base64 encoded in the notebook
            return data['image/png']

    return ''


def generate_html(caption_cells: List[Dict], chart_cells: List[Dict]) -> str:
    """Generate HTML with captions and charts side-by-side."""

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notebook Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .report-item {{
            background: white;
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            align-items: start;
        }}
        .caption {{
            padding-right: 20px;
        }}
        .caption h1 {{
            margin-top: 0;
            font-size: 1.8em;
            color: #333;
        }}
        .caption h2 {{
            margin-top: 0;
            font-size: 1.5em;
            color: #444;
        }}
        .caption h3 {{
            margin-top: 0;
            font-size: 1.2em;
            color: #555;
        }}
        .caption p {{
            color: #666;
            line-height: 1.6;
        }}
        .chart {{
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        @media (max-width: 768px) {{
            .report-item {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <h1 style="text-align: center; color: #333;">Notebook Report</h1>
{content}
</body>
</html>
"""

    content_items = []

    # Pair captions with charts
    max_items = max(len(caption_cells), len(chart_cells))

    for i in range(max_items):
        caption_html = ""
        chart_html = ""

        # Get caption if available
        if i < len(caption_cells):
            caption_source = ''.join(caption_cells[i].get('source', []))
            caption_html = markdown_to_html(caption_source)

        # Get chart if available
        if i < len(chart_cells):
            image_data = extract_image_from_cell(chart_cells[i])
            if image_data:
                chart_html = f'<img src="data:image/png;base64,{image_data}" alt="Chart {i+1}" />'

        # Create report item
        item_html = f"""    <div class="report-item">
        <div class="caption">
{caption_html}
        </div>
        <div class="chart">
{chart_html}
        </div>
    </div>
"""
        content_items.append(item_html)

    return html_template.format(content='\n'.join(content_items))


def main():
    """Main function to process the notebook and generate HTML."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <notebook_file.ipynb> [output.html]")
        sys.exit(1)

    notebook_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "report.html"

    # Validate input file
    if not Path(notebook_path).exists():
        print(f"Error: File not found: {notebook_path}")
        sys.exit(1)

    if not notebook_path.endswith('.ipynb'):
        print("Error: Input file must be a Jupyter notebook (.ipynb)")
        sys.exit(1)

    # Load and process notebook
    print(f"Loading notebook: {notebook_path}")
    notebook = load_notebook(notebook_path)

    print("Extracting tagged cells...")
    caption_cells, chart_cells = extract_tagged_cells(notebook)

    print(f"Found {len(caption_cells)} caption cell(s) and {len(chart_cells)} chart cell(s)")

    # Generate HTML
    print("Generating HTML report...")
    html_output = generate_html(caption_cells, chart_cells)

    # Write output file
    with open(output_path, 'w') as f:
        f.write(html_output)

    print(f"Report generated successfully: {output_path}")


if __name__ == "__main__":
    main()
