# AI Tours Hackathon

## Inspiration

Whenever I go to a new place, I try to learn more about the location.  If its a famous city, there are usually tours available, both online and in person.  
That's great, but what about everywhere else? I often find myself making a tour for myself in that case.  
With many tabs open trying to find information about my surrounding: map, Wikipedia, web search, it quickly gets overwhelming.  

This app solves this problem by giving you an AI as tour guide.

## What it does

An AI chat box is overlaid on top of beautiful 3D maps.  The AI knows your current location and begins the tour by zooming to your location on the map.  
The AI looks up your location and searches Wikipedia and Google Places to find information about your surroundings.  It gives you a nice tour of everything around you.

You are free to interact with your tour guide via chat.  You can ask questions about your location, or delve deeper into nearby points of interests.  
You can ask about the history of the city, or get demographics about the county.  

You ask about nearby stores, and the AI tells you that there is a large store in town.  The map glides to the location of the store and a big red, labeled pin is placed on it.

Your mind drifts and you start to wonder about Paris.  Wanting to explore, you ask the AI to take you to France.  The friendly tour guide whisks the map to the Eiffel tower,
giving an interesting historical account of its construction. You explore the surroundings some more, asking the guide for interesting factoids of the area.

## How its built

The app is a straightforward React front-end with a Python backend.  On load, the clientside attempts to get the user's goespacial coordinates.  
If successful, the coordinates are sent to the AI.  If not, user's IP address is used to get approximate coordinates.

The LLM agentic flow is implemented with help of the LangChain library.  The AI has access to multiple LangChain tools and is given a prompt to act as a tour guide.
The AI can call both frontend and backend tools.

The `reverse_geocode` tool allows the AI to translate a coordinate into city, county, or municipality.  Im using Google reverse geocode API with the address descriptors enhancement to implement this tool.
The `wikipedia` tool allows the AI to search for interesting information about the location.  AI can enter any text query to get any wiki page.
The `nearby_places` tool lets the AI to find places for a given coordinates.  Im using the new Google Places API to retrieve this information.
The AI can also call the `move_map` tool, which will move the 3D map to a new coordinate.  AI can provide a text label for the red pin that placed on this coordinate.
The frontend tools calls are sent to the client as a special stream payload.  When the client sees the map move command, I interact with the 3D map library to reposition the view and place a pin.

A deliberate focus on performance was taken while building the app.  Since LLMs can take a while to decide and use the available tools, streaming the AIs response is very important.
Server side events are used for AI responses and clientside tool calls.  A custom event schema is used to differentiate between chat chunks, tool calls, and final chat responses.  
AI response is animated on the client side.

## Challenges

LangChain agentic flows were a challenge.  I initially started with using LangServe library, since it promised an easy to setup chat backend.  However it soon became apparent that it was too complex and missing key features.
I ended up rolling a custom FastAPI server.  This allowed for better control of complexity and facilitated server side events.

Server side events were a challenge.  LangChain generates a lot of events during the LLM flow execution.  It took a while to find the right events to send to the SSE client.  
Animating the events as if it was being typed was also tricky.

## Accomplishments that we're proud of

The app is mobile responsive, so its nice to have the AI tour guide with me everywhere I go.  Its surprisingly fun to be able to explore the 3D maps and having an AI to chat with really lets me explore anywhere.

## What we learned

- streaming LLM via SSE
- implementing agentic tools
- 3D maps API is awesome

## What's next for AI Tours

This has been a fun hackathon, however the inherent time constraints let to a lot of features getting pushed out of scope.

I would like to add more tools to the AI, both backend and frontend.  On the backend, it would be nice to have more datasources.  
Google web search API, Yelp, bike and hiking trails, government goespacial datasets, and other datasets would be an awesome addition.

On the client side, I would like to use the 3D maps polygon and segment rendering features so the AI can draw directly on the map.

Chat persistence would be great.  Saving your chat history would allow for a tour to be tailored to the user even after the leave and come back.

Speech input would be great, especially in mobile. 
