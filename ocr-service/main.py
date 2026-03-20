import os
from fastapi import FastAPI, Request, BackgroundTasks
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrMacOptions

app = FastAPI()

# Use Apple's native Vision framework instead of Tesseract
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = OcrMacOptions() # This is the "M1 Turbo" button

converter = DocumentConverter()

def process_document(file_path: str, file_name: str):
    print(f"📄 Starting Docling conversion: {file_name}")
    try:
        # Convert TIFF to Docling's internal structured representation
        result = converter.convert(file_path)
        
        # Export to Markdown (best for LLMs/Processing) or JSON (best for mapping)
        content_md = result.document.export_to_markdown()
        
        # Save the result to your 'processing' folder
        output_path = f"./srv/sftpgo/processing/{file_name}.md"
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
        print(f"📥 Received Webhook Data: {data}") # Debug: See what SFTPGo is sending
        
        file_path = data.get("fs_path")
        file_name = data.get("object_name")

        # CRITICAL: Ensure the directory exists before starting
        os.makedirs("./srv/sftpgo/processing", exist_ok=True)

        background_tasks.add_task(process_document, file_path, file_name)
        return {"status": "queued"}
        
    except Exception as e:
        print(f"❌ Webhook Handler Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
