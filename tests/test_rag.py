"""Test script for RAG PDF extraction."""
import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment first
from dotenv import load_dotenv
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Now test PDF extraction directly
from io import BytesIO
import requests

def test_pdf_libraries():
    """Test which PDF libraries are available and working."""
    print("\n" + "="*60)
    print("Testing PDF Libraries")
    print("="*60 + "\n")
    
    # Check PyPDF2
    try:
        import PyPDF2
        print("✅ PyPDF2 installed:", PyPDF2.__version__)
    except ImportError as e:
        print("❌ PyPDF2 not available:", e)
    
    # Check pypdf
    try:
        import pypdf
        print("✅ pypdf installed:", pypdf.__version__)
    except ImportError as e:
        print("❌ pypdf not available:", e)
    
    # Check pdfplumber
    try:
        import pdfplumber
        print("✅ pdfplumber installed:", pdfplumber.__version__)
    except ImportError as e:
        print("❌ pdfplumber not available:", e)
    
    print("\n" + "="*60)
    print("Testing PDF Extraction from GitHub")
    print("="*60 + "\n")
    
    # Test URL - a sample PDF from GitHub
    test_url = "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/basicapi.pdf"
    
    try:
        print(f"Downloading test PDF from: {test_url}")
        response = requests.get(test_url, timeout=10)
        response.raise_for_status()
        print(f"✅ Downloaded {len(response.content)} bytes\n")
        
        pdf_content = response.content
        
        # Try PyPDF2 with strict=False
        try:
            import PyPDF2
            print("Testing PyPDF2 extraction (strict=False)...")
            pdf_file = BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf_file, strict=False)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
            print(f"✅ PyPDF2: Extracted {len(text)} characters")
            print(f"   First 100 chars: {text[:100]}")
        except Exception as e:
            print(f"❌ PyPDF2 failed: {e}")
        
        # Try pypdf
        try:
            import pypdf
            print("\nTesting pypdf extraction...")
            pdf_file = BytesIO(pdf_content)
            reader = pypdf.PdfReader(pdf_file)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
            print(f"✅ pypdf: Extracted {len(text)} characters")
            print(f"   First 100 chars: {text[:100]}")
        except Exception as e:
            print(f"❌ pypdf failed: {e}")
        
        # Try pdfplumber
        try:
            import pdfplumber
            print("\nTesting pdfplumber extraction...")
            pdf_file = BytesIO(pdf_content)
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            print(f"✅ pdfplumber: Extracted {len(text)} characters")
            print(f"   First 100 chars: {text[:100]}")
        except Exception as e:
            print(f"❌ pdfplumber failed: {e}")
            
    except Exception as e:
        print(f"❌ Failed to download test PDF: {e}")

if __name__ == "__main__":
    test_pdf_libraries()
