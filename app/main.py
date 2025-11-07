from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.agent import RealEstateAgent
from fastapi import File, UploadFile, Request
from app.upload_agent import UploadAgent
import tempfile
import os
from pydantic import BaseModel
import ast

# Instantiate upload agent
upload_agent = UploadAgent()

class QueryRequest(BaseModel):
    query: str
    
class PropertyInput(BaseModel):
    text: str

app = FastAPI(title="Real Estate Agentic AI")


# Initialize the main agent instance
# python -m uvicorn app.main:app --reload
agent = RealEstateAgent()

# Mount the static directory for assets
app.mount("/static", StaticFiles(directory="ui"), name="static")

@app.get("/")
def home():
    return FileResponse("ui/index.html")

#show me 3bhk flat in noida location for the budget 2 crore
@app.post("/query")
async def handle_query(data: QueryRequest):
    """Accepts text query from user."""
    response = await agent.handle_query(data.query)
    return {
        "query": data.query,
        "count": {len(response["properties"])},
        "properties": response["properties"],
        #"summarize":response["summarize"]
        "summarize":ast.literal_eval(response["summarize"])["choices"][0]["message"]["content"]
    }
    #return {"response": response}


@app.post("/voice-query")
async def handle_voice_query(audio_file: bytes = Form(...)):
    """Accepts a voice query (to be processed by STT)."""
    print(audio_file)
    audio_bytes = await audio_file.read()
    
        
    text_query = agent.stt_to_text(audio_bytes)
    response = await agent.handle_query(text_query)
    
    return {"query": text_query, "response": response}

@app.post("/voice-query-upload")
async def handle_voice_query(audio_file: UploadFile = File(...)):
    """Accepts a voice query (to be processed by STT)."""
    audio_bytes = await audio_file.read()
    text_query = agent.stt_to_text(audio_bytes)
    response = await agent.handle_query(text_query)
    return {"query": text_query, "response": response}

@app.post("/upload-property")
async def upload_property(input_data: PropertyInput, request: Request):
    """
    Accepts paragraph-style text input describing a property.
    Example body:
    {
      "text": "I want to list a 2BHK flat in Noida for 75 lakh, 950 sqft, with parking and lift."
    }
    """
    text = input_data.text
    session_id = request.headers.get("session-id", "default-user")
    print("Input details for upload")
    print(text)
    result = await upload_agent.process_input(text, session_id)
    return result


@app.post("/reset-session")
async def reset_session(request: Request):
    """Resets property upload memory for a session"""
    session_id = request.headers.get("session-id", "default-user")
    upload_agent.memory.clear(session_id)
    return {"status": "reset", "message": "Session cleared. You can start fresh."}