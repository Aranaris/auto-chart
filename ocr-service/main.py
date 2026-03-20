from fastapi import FastAPI, Request
import os

app = FastAPI()

# This is where your sFTP files actually live on the host
DATA_DIR = "./srv/sftpgo/data/fax-inbound"

@app.post("/process-fax")
async def handle_sftp_event(request: Request):
    # SFTPGo sends the event data as JSON in the body
    data = await request.json()
    
    # We care about the 'fs_path' (the actual path on disk)
    file_path = data.get("fs_path")
    file_name = data.get("object_name")
    
    if not file_path or not file_name.lower().endswith(('.tiff', '.tif')):
        return {"status": "ignored", "reason": "not a tiff file"}

    print(f"🚀 New fax received: {file_name}")
    
    # NEXT STEP: Trigger your OCR function here
    # result = run_ocr(file_path)
    
    return {"status": "success", "message": f"Processing {file_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
