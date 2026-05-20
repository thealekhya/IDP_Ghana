import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env variables early
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

from backend.agent.graph import agent

app = FastAPI(title="Sankofa AI API")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    citations: list

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        print(f"Received query: {request.query}")
        result = agent.invoke({
            "query": request.query,
            "messages": [],
        })
        
        # We need to return both the final answer and the structured citations
        final_answer = result.get("final_answer", "I couldn't generate an answer.")
        if final_answer == "ERROR_QUOTA_EXCEEDED":
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please recharge your quota.")
            
        # If citations isn't in the state or is empty, provide an empty list
        citations = result.get("citations") or []
        
        return ChatResponse(
            answer=final_answer,
            citations=citations
        )
    except HTTPException:
        # Re-raise HTTPExceptions as is (e.g. our 429 Quota Exceeded)
        raise
    except Exception as e:
        print(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Make sure setup has run (so databases exist) before starting API
    from backend.app import setup
    setup()
    print("Starting API Server on port 8000...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
