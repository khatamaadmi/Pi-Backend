import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from dotenv import load_dotenv
from groq import Groq
from prompts import get_system_prompt

load_dotenv()
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    topic: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        completion = groq.chat.completions.create(
            messages=[{"role": "system", "content": get_system_prompt(request.topic)}, *formatted_messages],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=1000,
        )
        print(completion.choices[0].message.content)
        response_message = completion.choices[0].message.content or "I couldn't generate a response."

        return ChatResponse(response=response_message)
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")


@app.get("/")
async def root():
    return {"message": "Server is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )


