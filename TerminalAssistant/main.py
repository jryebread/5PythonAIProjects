#!/usr/bin/env python
#termy
from dotenv import load_dotenv
load_dotenv()
import os
import argparse
import openai

OPENAI_KEY = os.getenv('OPENAI_KEY')

def generate_prompt(message):
    return ("""The following is a conversation with an AI assistant. 
    'The assistant helps programmers answer questions about terminal commands.
Human: Hello, who are you?
AI: I am an AI named termy created to answer terminal related questions. How can I help you today?
Human: """ + message)

def get_ai_response(msg):
    response = openai.Completion.create(
      api_key=OPENAI_KEY,
      model="text-davinci-003",
      prompt=generate_prompt(msg),
      temperature=0.1,
      max_tokens=100,
    )
    return response


p = argparse.ArgumentParser()
p.add_argument('query')

args = p.parse_args()
print(args.query)

response = get_ai_response(args.query)
print(response["choices"][0]["text"])









