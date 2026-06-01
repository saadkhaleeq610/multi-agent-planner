import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from langchain_groq import ChatGroq
from graph import stream_plan

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)


class GoalRequest(BaseModel):
    goal: str


@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")


@app.post("/plan")
async def plan(request: GoalRequest):
    async def event_generator():
        try:
            async for update in stream_plan(request.goal, llm):
                yield {"data": json.dumps(update)}
            yield {"data": json.dumps({"agent": "done", "output": ""})}
        except Exception as e:
            yield {"data": json.dumps({"agent": "error", "output": str(e)})}

    return EventSourceResponse(event_generator())


app.mount("/static", StaticFiles(directory="../frontend"), name="static")
