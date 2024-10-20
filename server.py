import asyncio
import json
from types import NoneType
from typing import AsyncIterable



from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from sse_starlette import EventSourceResponse
import uvicorn
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from geocode_tools import reverse_geocode
import pprint
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import geocoder


RETRY_TIMEOUT = 15000 #15s

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HistoryMessage(BaseModel):
    content: str
    role: str

class Message(BaseModel):
    content: str
    user_location: str
    history: list[HistoryMessage]


async def send_message(content: str, user_location: str, history: list[HistoryMessage]) -> AsyncIterable[str]:
    model = ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        verbose=True,
    )
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    tools = [reverse_geocode, wikipedia]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are an amazing tour guide that can give tours of any location in the world.
                Use the reverse_geocode tool to get the locality, county, and state of the given coordinates.
                Use wikipedia tool to lookup each of these. 
                The user location is {user_location}.
                Begin the tour by telling the user about the location they are in.
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    chat_history = []
    for message in history:
        chat_history.append((message.role, message.content))


    id = 0
    async for chunk in agent_executor.astream_events({"input": content, "user_location": user_location, "chat_history": chat_history}, version="v1"):
        # print("------")
        # pprint.pprint(chunk, depth=3)
        name = chunk["name"]
        data = chunk["data"]
        event = chunk["event"]
        if event == "on_chain_end" and name == "AgentExecutor":
            yield {"event": event,"id": id,"retry": RETRY_TIMEOUT,"data": data["output"]["output"]}
            id += 1



@app.post("/stream/")
async def stream_chat(message: Message):
    generator = send_message(message.content, message.user_location, message.history)
    return EventSourceResponse(generator)

@app.get("/ipcoords/")
async def get_coords(request: Request):
    client_host = request.client.host
    if client_host == "127.0.0.1":
        client_host = "172.56.168.99"
    g = geocoder.ip(client_host)
    if isinstance(g, NoneType) or len(g.latlng) == 0:
        return {"error": "Could not get coordinates"}
    return {"lat": g.latlng[0], "lng": g.latlng[1]}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)