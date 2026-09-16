import os
from google import genai

client = genai.Client(api_key="DUMMY")
chat = client.chats.create(model="gemini-2.5-flash")
print(dir(chat))
