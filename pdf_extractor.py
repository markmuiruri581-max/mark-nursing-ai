import pdfplumber
import os
import requests
import tempfile
from urllib.parse import urlparse

def is_url(path):
    """Helper function to check if the provided string is a valid URL."""
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_text_from_pdf(pdf_path_or_url):
    """
    Extracts text from a local PDF file or a web URL.
    Downloads online PDFs temporarily for extraction.
    """
    try:
        full_text = ""
        
        # Branch 1: The input is a web URL
        if is_url(pdf_path_or_url):
            print(f"🌐 Downloading online PDF from: {pdf_path_or_url}")
            
            # Stream the download to handle large clinical PDFs efficiently
            response = requests.get(pdf_path_or_url, stream=True)
            response.raise_for_status() # Trigger an error if the download fails
            
            # Create a temporary file that automatically cleans up later
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_pdf.write(chunk)
                temp_pdf_path = temp_pdf.name
            
            # Extract text from the temporary file
            with pdfplumber.open(temp_pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                        
            # Clean up the temporary file from the system
            os.remove(temp_pdf_path)
            
        # Branch 2: The input is a local file path
        else:
            print(f"📂 Extracting local PDF from: {pdf_path_or_url}")
            with pdfplumber.open(pdf_path_or_url) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                        
        return full_text
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error downloading PDF: {e}"
    except Exception as e:
        return f"❌ Error extracting PDF: {e}"