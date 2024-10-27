from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class CodeAnalysisRequest(BaseModel):
    code: Optional[str] = None
    url: Optional[str] = None
    file_content: Optional[str] = None

@app.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    if request.code:
        return {"message": "Analyzing code...", "code": request.code}
    elif request.url:
        return {"message": "Analyzing URL...", "url": request.url}
    elif request.file_content:
        return {"message": "Analyzing file...", "file_content": request.file_content}
    else:
        return {"error": "No input provided. Please provide code, URL, or file content."}
