import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, JARVIS_SYSTEM_PROMPT, MODEL_NAME
from actions.system import SystemActions
from actions.developer import execute_command, read_file, write_file
from config import APP_ALIASES

class JarvisBrain:
    def __init__(self):
        self.system_actions = SystemActions(APP_ALIASES)
        self.chat = None
        self.client = None

        # Gather all tools to expose to Gemini
        self.tools = [
            self.system_actions.get_system_metrics,
            self.system_actions.launch_app,
            self.system_actions.adjust_volume,
            execute_command,
            read_file,
            write_file
        ]

        # Only initialize if we have an API key (allows testing without key)
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.init_chat()
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")

    def init_chat(self):
        if not self.client:
            return

        try:
            self.chat = self.client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=JARVIS_SYSTEM_PROMPT,
                    temperature=0.7,
                    tools=self.tools
                )
            )
        except Exception as e:
            print(f"Failed to initialize chat: {e}")

    def process_input(self, user_input: str) -> str:
        """Processes user input using Gemini and handles tool calls."""
        if not self.chat:
            return "Sinir ağından bağlantım kopmuş gibi görünüyor, efendim. Lütfen API anahtarını kontrol edin."

        try:
            response = self.chat.send_message(user_input)

            # If the response text is empty, it might mean the model only returned function calls (although the python SDK often handles this transparently).
            # The google-genai SDK's chat session automatically handles tool calls behind the scenes!
            # It will execute the python functions we passed in `tools` and send the results back to the model.
            # We just return the final text response.

            if response.text:
                return response.text
            else:
                return "Araç çalıştırıldı, efendim. Görevi tamamladım."

        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Şu anda bunu işlemekte zorlanıyorum, efendim."
