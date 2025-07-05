
from agents import Runner, Agent, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
import os
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

backend_agent = Agent(
    name="Backend Expert",
    instructions="""
You are a backend development expert. You help users with backend topics like APIs, databases, authentication, server frameworks (e.g., Express.js, Django).

Do NOT answer frontend or UI questions.
"""
)

frontend_agent = Agent(
    name="Frontend Expert",
    instructions="""
You are a frontend expert. You help with UI/UX using HTML, CSS, JavaScript, React, Next.js, and Tailwind CSS.

Do NOT answer backend-related questions.
"""
)

web_dev_agent = Agent(
    name="Web Developer Agent",
    instructions="""
You are a generalist web developer who decides whether a question is about frontend or backend.

If the user asks about UI, HTML, CSS, React, etc., hand off to the frontend expert.
If the user asks about APIs, databases, servers, backend frameworks, etc., hand off to the backend expert.
If it’s unrelated to both, politely decline.
""",
    handoffs=[
        frontend_agent,
        backend_agent
    ]
)

@cl.on_chat_start
async def handle_start_chat():
    cl.user_session.set("history", [])
    await cl.Message(content="👋 Hello from Tehreem Fatima ! Ask anything about web dev.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    history.append({"role": "user", "content": message.content})
    
    msg= cl.Message(content="")
    await msg.send()
    # 🔄 RUN the web_dev_agent, NOT frontend_agent directly
    result = Runner.run_streamed(
        web_dev_agent,
        input=history,
        run_config=config
    )
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)


    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

