import json
from typing import Annotated
from fastapi import Body, Depends, FastAPI
from openai import OpenAI
from app.settings import OPENAI_API_KEY
from app.models import CategoryDemo
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session , create_engine, select
from app.settings import DATA_BASE_URL

engine = create_engine(url=DATA_BASE_URL , echo=True)

def create_table():
    SQLModel.metadata.create_all(engine)

client = OpenAI(api_key=OPENAI_API_KEY)

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_table()
    yield

app = FastAPI(lifespan=lifespan)


def get_session():
    with Session(engine) as session:
        yield session

"""
get todo task
paramter task
"""

def get_category():
 with Session(engine) as session:
    result = session.exec(select(CategoryDemo)).all()
    categoryes  = []
    for category in result:
        categoryes.append(category.model_dump())
    return json.dumps(categoryes)


def get_location(name : str):
    if name == "zia khan":
        return "Islamabad"
    elif name == "Junaid":
        return "Lahore"
    elif name == "Sir Qasim":
        return "Karachi"
    else:
        return "Location not found"
    

def run_conversation(prompt:str):
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": prompt}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_location",
                "description": "Get the Location of given person",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name  of the person",
                        },
                    },
                    "required": ["name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_category",
                "description": "Get the Category",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_location": get_location,
            "get_category":get_category
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name] #get_location
            function_args = json.loads(tool_call.function.arguments)
            print(function_args)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content



@app.get('/' , tags=["Root Route"])
def root_route():
    return {"message":"Learn Openai"}


@app.post('/get-location')
def get_location_route(prompt:Annotated[str , Body(...)]):
    return run_conversation(prompt=prompt)


@app.post('/get-catagory')
def get_catagory(prompt : str):
    return run_conversation(prompt=prompt)


@app.post('/add-category' , response_model=CategoryDemo)
def add_category(data : CategoryDemo , session:Annotated[Session , Depends(get_session)]):
    session.add(data)
    session.commit()
    session.refresh(data)
    return data