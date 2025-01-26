from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import logging
from fixation import analyzeURL, analyzeCode, analyzeCodeFromFile
from chat import ChatGPT 

app = FastAPI()

logging.basicConfig(level=logging.INFO)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeAnalysisRequest(BaseModel):
    code: str

class UrlAnalysisRequest(BaseModel):
    url: str
    
class ChatQuery(BaseModel):
    code: str

chat_gpt = ChatGPT()

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
async def analyze_file(file: UploadFile = File(...)):
    try:
        logging.info(f"Received file content for analysis: {file.filename}")
        content = await file.read()
        result = analyzeCodeFromFile(content, file.filename)
        return result
    except Exception as e:
        logging.error(f"Error analyzing file content: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


@app.post("/chat")
async def chat_response(query: ChatQuery):
    try:
        response = await chat_gpt.generate_response(query.code)
        return {"text": response}
    except Exception as e:
        print(f"Error: {str(e)}") 
        return {"error": str(e)}