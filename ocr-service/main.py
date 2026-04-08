import os
import shutil
import datetime

from fastapi import FastAPI, Request, BackgroundTasks
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions
from dotenv import load_dotenv
from fhir_mapper import create_fhir_patient


# Load variables from .env into the system environment
load_dotenv()

# Use the variables with fallbacks (defaults)
INBOUND_DIR = os.getenv("INBOUND_DIR", "./data/inbound")
OUTBOUND_DIR = os.getenv("OUTBOUND_DIR", "./data/processing")
ARCHIVE_DIR = os.path.join(os.path.dirname(INBOUND_DIR), "archive")
APP_PORT = int(os.getenv("APP_PORT", 8000))

app = FastAPI()

# Use Apple's native Vision framework instead of Tesseract
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = OcrMacOptions()  # This is the "M1 Turbo" button

converter = DocumentConverter()

def process_document(file_path: str, file_name: str):
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
        # NEXT STEP: Trigger the FHIR Mapper

        extracted_data = {
            "name": "John Doe",
            "dob": "05/15/1985",
            "gender": "Male",
            "ssn": "000-00-0000"
            }

        fhir_json = create_fhir_patient(extracted_data)
        with open(f"{OUTBOUND_DIR}/patient_fhir.json", "w") as f:
            f.write(fhir_json)

        # 2. Archive the file with a timestamp
        archived_filename = f"{file_root}_{timestamp}{ext}"
        
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        archive_path = os.path.join(ARCHIVE_DIR, archived_filename)
        
        shutil.move(file_path, archive_path)
        print(f"✅ Success! Moved to archive: {archived_filename}")
        
    except Exception as e:
        print(f"❌ Docling failed on {file_name}: {e}")

@app.post("/process-fax")
async def handle_event(request: Request, background_tasks: BackgroundTasks):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
