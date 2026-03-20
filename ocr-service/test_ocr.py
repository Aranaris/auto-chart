import os
from docling.document_converter import DocumentConverter

# 1. Point this to one of the test faxes we created earlier
# Ensure this path matches where you saved your sample_fax.tiff
IMAGE_PATH = "../srv/sftpgo/data/fax-inbound/sample_fax.tiff"

def run_test():
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Error: Could not find file at {IMAGE_PATH}")
        return

    print(f"🔍 Analyzing {IMAGE_PATH}...")
    
    # 2. Initialize the converter
    # Docling automatically detects if it should use Tesseract or Apple Vision
    converter = DocumentConverter()
    
    try:
        # 3. Perform the conversion
        result = converter.convert(IMAGE_PATH)
        
        # 4. Export to Markdown to see the structure
        markdown_output = result.document.export_to_markdown()
        
        print("\n--- OCR OUTPUT START ---")
        print(markdown_output)
        print("--- OCR OUTPUT END ---\n")
        
        print("✅ Success! Docling identified the text and layout.")
        
    except Exception as e:
        print(f"❌ Docling conversion failed: {e}")

if __name__ == "__main__":
    run_test()
