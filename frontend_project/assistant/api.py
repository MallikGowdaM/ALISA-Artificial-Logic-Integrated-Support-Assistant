# virtual-assistant-backend/api.py
from fastapi import FastAPI
from pydantic import BaseModel
import main  # this is your main.py which connects to all other modules

app = FastAPI()

class Query(BaseModel):
    input: str
    lang: str = "en"

@app.post("/ask")
async def ask(query: Query):
    """
    Endpoint to handle user queries.
    """
    try:
        result = main.handle_single_command(query.input, lang=query.lang)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# Example: add more endpoints if needed
@app.get("/health")
async def health_check():
    return {"status": "ok"}
