from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import logging
from fixation import analyzeURL, analyzeCode, analyzeCodeFromFile

app = FastAPI()

logging.basicConfig(level=logging.INFO)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; specify if necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


class CodeAnalysisRequest(BaseModel):
    code: str

class UrlAnalysisRequest(BaseModel):
    url: str

class FileAnalysisRequest(BaseModel):
    content: str

@app.post("/analyzeCode")
async def analyze_code(request: CodeAnalysisRequest):
    try:
        logging.info(f"Received code for analysis: {request.code}")
        result = analyzeCode(request.code)
        return result
    except Exception as e:
        logging.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyzeUrl")
async def analyze_url(request: UrlAnalysisRequest) -> Any:
    try:
        logging.info(f"Received URL for analysis: {request.url}")
        result = analyzeURL(request.url)
        return result
    except Exception as e:
        logging.error(f"Error analyzing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyzeFile")
async def analyze_file(request: FileAnalysisRequest):
    try:
        logging.info(f"Received file content for analysis: {request.content}")
        result = analyzeCodeFromFile(request.content)
        return result
    except Exception as e:
        logging.error(f"Error analyzing file content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
