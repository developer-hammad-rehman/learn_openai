from fastapi import FastAPI
from openai import OpenAI
from fastapi.responses import StreamingResponse
from app.settings import OPENAI_API_KEY
from contextlib import asynccontextmanager

client = OpenAI(api_key=OPENAI_API_KEY)

@asynccontextmanager
async def lifespan(app:FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

def event_openai_stream():
     reponse  = client.chat.completions.create(
        messages=[
            {"role":"user" , "content":"write me an essay"}
        ],
        model="gpt-3.5-turbo",
        stream=True
    )
     for part in reponse:
        content = part.choices[0].delta.content or ""
        if content:
         yield content

@app.get('/' , tags=["Route Route"])
def root_route():
    event_openai_stream()
    return {"message" : "Learn Openai"}


# def event_demo_stream():
#     message = ["learn genai\n" , "learn nextjs\n" , "learn openai\n" , "Learn fastapi\n" , "learn typescrpit\n" , "Machine Learning"]
#     for msg in message:
#         yield msg


# @app.get('/demo-stream')
# def demo_streaming_route():
#     return StreamingResponse(event_demo_stream() , media_type="text/plain")


@app.get('/stream_opeanai')
def opeani_straming_function():
    return StreamingResponse(event_openai_stream() , media_type="text/plain")