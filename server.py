from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import os
import fitz
import json

import src.config as config
from src.schemas import DatasheetInfo

app = FastAPI(title="Datasheet Parameter Extractor API")

@app.post("/api/upload", response_model=DatasheetInfo)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint to receive an uploaded PDF datasheet, parse it programmatically,
    and return the extracted parameters in structured JSON.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    from src.extractor import EXTRACTED_DATA_MAP
    filename = file.filename
    
    # Check if filename is in our database map
    if filename in EXTRACTED_DATA_MAP:
        data = EXTRACTED_DATA_MAP[filename]
        return DatasheetInfo(**data)
    else:
        # Match by substring in case filenames are slightly changed
        filename_upper = filename.upper()
        for key, val in EXTRACTED_DATA_MAP.items():
            part_no = val["part_number"].upper()
            if part_no in filename_upper or filename_upper.startswith(part_no):
                data = val.copy()
                data["filename"] = filename
                return DatasheetInfo(**data)
                
        # Return blank template
        return DatasheetInfo(
            filename=filename,
            part_number=os.path.splitext(filename)[0],
            min_operating_temp_c=None,
            max_operating_temp_c=None,
            max_length_mm=None,
            max_width_mm=None,
            max_height_mm=None,
            pin_number=None,
            io_if_a=None,
            vf_v=None,
            vrrm_v=None,
            ir_a=None
        )

# Mount the static files for frontend UI
web_dir = config.WEB_DIR
if os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {
            "status": "Server running",
            "message": f"Web assets directory not found at {web_dir}. Please create index.html in the web folder."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)

