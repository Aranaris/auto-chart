import os
from fastapi import FastAPI, Request, BackgroundTasks
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions
from dotenv import load_dotenv

# Load variables from .env into the system environment
load_dotenv()

# Use the variables with fallbacks (defaults)
INBOUND_DIR = os.getenv("INBOUND_DIR", "./data/inbound")
OUTBOUND_DIR = os.getenv("OUTBOUND_DIR", "./data/processing")
APP_PORT = int(os.getenv("APP_PORT", 8000))

app = FastAPI()

# Use Apple's native Vision framework instead of Tesseract
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = OcrMacOptions()  # This is the "M1 Turbo" button

converter = DocumentConverter()

def process_document(file_path: str, file_name: str):
    print(f"📄 Starting Docling conversion: {file_name}")
    try:
        # Convert TIFF to Docling's internal structured representation
        result = converter.convert(file_path)

        # Export to Markdown (best for LLMs/Processing) or JSON (best for mapping)
        content_md = result.document.export_to_markdown()

        # Save the result to your 'processing' folder
        file_root, _ = os.path.splitext(file_name)
        outbound_file_name = f"{file_root}.md"
        output_path = os.path.join(OUTBOUND_DIR, outbound_file_name)
        with open(output_path, "w") as f:
            f.write(content_md)

        print(f"✅ Conversion complete: {output_path}")
        # NEXT STEP: Trigger the FHIR Mapper
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
