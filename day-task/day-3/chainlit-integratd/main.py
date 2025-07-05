from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI,set_tracing_disabled,RunConfig
from dotenv import load_dotenv
import os
import chainlit as cl

# Load environment variables
load_dotenv()

# Disable tracing if needed
set_tracing_disabled(True)

# Set up Gemini API client
gemini_api_key = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Set up model using the external Gemini client
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)


config = RunConfig(
    model=model,
    # model_provider=extarnal_client,
    tracing_disabled=True
)
agent = Agent(
    name="naina agent",
    instructions="You are a helpful assistant. Remember what the user tells you.",
    model=model,
      # ← MEMORY SET HERE
)

@cl.on_message

async def hendel_message(message : cl.Message):

    result = await Runner.run(
        agent,
        input=message.content
    )
    await cl.Message(content=result.final_output).send()
 
