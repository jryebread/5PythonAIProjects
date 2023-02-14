# This example requires the 'message_content' intent.
import os
from dotenv import load_dotenv
load_dotenv()

import openai

import discord
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')
# https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro

def generate_prompt(message):
    return ("""The following is a conversation with an AI assistant. 
    'The assistant is helpful, creative, clever, and very sarcastic.
Human: Hello, who are you?
AI: I am an AI created by Tony Stark. How can I help you today?
Human: """ + message)

def get_ai_response(msg):
    response = openai.Completion.create(
      api_key=OPENAI_KEY,
      model="text-davinci-003",
      prompt=generate_prompt(msg),
      temperature=0.6,
      max_tokens=100,
    )
    return response

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('i like pineapple on pizza')
        return
    response = get_ai_response(message.content)
    await message.channel.send(response["choices"][0]["text"])

    return

client.run(BOT_TOKEN)