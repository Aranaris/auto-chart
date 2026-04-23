import os
import shutil
import datetime
import fastapi

from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions
from dotenv import load_dotenv, find_dotenv

# Load variables from .env into the system environment
load_dotenv(find_dotenv())

if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ Warning: GOOGLE_API_KEY not found in environment!")

from fhir_mapper import extract_to_fhir

# Use the variables with fallbacks (defaults)
INBOUND_DIR = os.getenv("INBOUND_DIR", "./data/inbound")
OUTBOUND_DIR = os.getenv("OUTBOUND_DIR", "./data/processing")
ARCHIVE_DIR = os.path.join(os.path.dirname(INBOUND_DIR), "archive")
APP_PORT = int(os.getenv("APP_PORT", 8000))

app = fastapi.FastAPI()

# Use Apple's native Vision framework instead of Tesseract
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = OcrMacOptions()  # This is the "M1 Turbo" button

converter = DocumentConverter()

async def process_document(file_path: str, file_name: str):
    print(f"📄 Starting Docling conversion: {file_name}")
    file_root, ext = os.path.splitext(file_name)

    if ext not in [".tiff", ".tiff", ".pdf"]:
        print(f"Skipping unsupported filetype: .{ext}")
        return
    
    try:
        # Convert TIFF to Docling's internal structured representation
        result = converter.convert(file_path)

        # Export to Markdown (best for LLMs/Processing) or JSON (best for mapping)
        content_md = result.document.export_to_markdown()

        # Save the result to your 'processing' folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        output_file_name = f"{file_root}_{timestamp}.md"

        output_path = os.path.join(OUTBOUND_DIR, output_file_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content_md)

        print(f"✅ Conversion complete: {output_path}")
        # 2. Trigger the FHIR Mapper

        fhir_patient_json = await extract_to_fhir(content_md)
        fhir_output_path = f"{OUTBOUND_DIR}/patient_fhir.json"
        with open(fhir_output_path, "w") as f:
            f.write(fhir_patient_json)

        print(f"✅ FHIR Mapping Complete: {fhir_output_path}")

        # 3. Archive the file with a timestamp
        archived_filename = f"{file_root}_{timestamp}{ext}"
        
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        archive_path = os.path.join(ARCHIVE_DIR, archived_filename)
        
        shutil.move(file_path, archive_path)
        print(f"✅ Success! Moved to archive: {archived_filename}")
        
    except Exception as e:
        print(f"❌ Docling failed on {file_name}: {e}")

@app.post("/process-fax")
async def handle_event(request: fastapi.Request, background_tasks: fastapi.BackgroundTasks):
    try:
        data = await request.json()
        print(f"📥 Received Webhook Data: {data}")  # Debug: See what SFTPGo is sending
        
        file_name = data.get("object_name")
        file_path = os.path.join(INBOUND_DIR, file_name)

        # CRITICAL: Ensure the directory exists before starting
        os.makedirs(f"{OUTBOUND_DIR}", exist_ok=True)

        background_tasks.add_task(process_document, file_path, file_name)
        return {"status": "queued"}

    except Exception as e:
        print(f"❌ Webhook Handler Failed: {str(e)}")
        return {"status": "error", "message": str(e)}
    
import re

def extract_field(pattern, text, default="Unknown"):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else default

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
