# About 

This tiny project is a PoC to show how simple it is to extract info from Jupyter Notebooks

The script main.py processes a ipynb file and creates:
- A responsive HTML layout with captions on the left and charts on the right
- Mobile-friendly design (stacks vertically on small screens)
- Clean styling with proper typography and spacing
- Base64-encoded images embedded directly in the HTML (no external files needed)

# How

The script (main.py) does the following:

  1. Reads Jupyter notebooks as JSON files
  2. Extracts cells tagged with `caption` (markdown) and `chart` (code with image outputs)
  3. Converts markdown to HTML (basic conversion included)
  4. Generates a static HTML report with captions and charts displayed side-by-side in a clean, responsive layout

  Usage

  ```python main.py Sample.ipynb```

Outputs to report.html (default)




 