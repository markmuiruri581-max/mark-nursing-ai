import markdown
import os

# The CSS Template designed for a professional, clinical study guide look
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #2c3e50; /* Deep blue/slate for clinical feel */
            --secondary-color: #3498db; /* Bright blue for accents */
            --bg-color: #f4f7f6; /* Soft gray background to reduce eye strain */
            --text-color: #333333;
            --border-color: #cbd5e1;
        }}
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .container {{
            background-color: #ffffff;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: var(--primary-color);
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        h1 {{ 
            border-bottom: 3px solid var(--secondary-color); 
            padding-bottom: 0.5rem; 
        }}
        h2 {{ 
            border-bottom: 1px solid var(--border-color); 
            padding-bottom: 0.3rem; 
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.95em;
        }}
        th, td {{
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            text-align: left;
        }}
        th {{
            background-color: var(--primary-color);
            color: #ffffff;
            font-weight: bold;
        }}
        tr:nth-child(even) {{ 
            background-color: #f8fafc; 
        }}
        blockquote {{
            border-left: 5px solid var(--secondary-color);
            margin: 1.5rem 0;
            padding: 1rem 1.5rem;
            background-color: #eaf2f8;
            font-style: italic;
            border-radius: 0 4px 4px 0;
        }}
        code {{
            background-color: #f1f5f9;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: Consolas, monospace;
            color: #e74c3c;
        }}
        pre code {{
            display: block;
            padding: 1rem;
            overflow-x: auto;
            background-color: #2c3e50;
            color: #f8f8f2;
        }}
        
        /* --- MOBILE RESPONSIVE TWEAKS --- */
        @media (max-width: 768px) {{
            body {{
                padding: 0.5rem; /* Shrink outer gray borders */
            }}
            .container {{
                padding: 1.5rem; /* Shrink inner white padding */
                border-radius: 6px;
            }}
            table {{
                display: block; /* Allows the table to take up its own block space */
                overflow-x: auto; /* Enables horizontal scrolling for wide tables */
                white-space: nowrap; /* Prevents text from wrapping awkwardly in tight columns */
            }}
            th, td {{
                padding: 10px; /* Slightly tighter table cells */
            }}
            h1 {{
                font-size: 1.75rem; /* Scale down main headers */
            }}
            h2 {{
                font-size: 1.4rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

def convert_text_to_html(markdown_text, title="Study Document"):
    """
    Converts raw markdown text to styled HTML using the clinical template.
    """
    # The 'extra' extension enables tables, fenced code blocks, and more.
    html_content = markdown.markdown(
        markdown_text,
        extensions=['extra', 'sane_lists', 'nl2br']
    )
    # Inject the generated HTML into our CSS template
    return HTML_TEMPLATE.format(title=title, content=html_content)

def render_markdown_file(input_filepath, output_filepath, title="Study Document"):
    """
    Reads a markdown file, converts it to styled HTML, and saves the new file.
    """
    try:
        # Read the plain Markdown file
        with open(input_filepath, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Convert it
        final_html = convert_text_to_html(md_text, title)
        
        # Save the new HTML file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)
            
        print(f"✅ Successfully rendered visual HTML: {os.path.basename(output_filepath)}")
        return True
    except Exception as e:
        print(f"❌ Error rendering {input_filepath}: {e}")
        return False

if __name__ == "__main__":
    print("Renderer module is ready. Import this script to use its functions.")