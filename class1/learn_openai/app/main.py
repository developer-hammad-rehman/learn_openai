from fastapi import FastAPI
from openai import OpenAI
from app.settings import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="Learn Openai")


@app.get("/")
def root_route():
    return "Welcome To opeani...."


@app.get("/get-openai")
def opeani_route():
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={ "type": "json_object" },
        messages=[
        {"role":"system" , "content":"You have to act like the test api give output in JSON."}, 
        {"role": "user", "content": "Say Hello World"}
        ],
    )
    return json.loads(response.choices[0].message.content)