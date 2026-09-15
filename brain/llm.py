import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, JARVIS_SYSTEM_PROMPT
from actions.system import SystemActions
from config import APP_ALIASES

class JarvisBrain:
    def __init__(self):
        self.system_actions = SystemActions(APP_ALIASES)
        self.chat = None
        self.client = None

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
                model="gemini-1.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=JARVIS_SYSTEM_PROMPT,
                    temperature=0.7,
                )
            )
        except Exception as e:
            print(f"Failed to initialize chat: {e}")

    def process_input(self, user_input: str) -> str:
        """Processes user input, handles system commands, and returns the response."""
        input_lower = user_input.lower()

        # Intercept simple commands for system actions
        if "what are my system stats" in input_lower or "cpu" in input_lower or "ram" in input_lower:
            cpu, ram = self.system_actions.get_system_metrics()
            return f"Sir, CPU usage is currently at {cpu} percent, and RAM usage is at {ram} percent."

        if "open" in input_lower or "launch" in input_lower:
            import re
            match = re.search(r'(open|launch) (.+)', input_lower)
            if match:
                # E.g. "open visual studio code" -> "visual studio code"
                target = match.group(2).strip().strip('.').strip('?')
                success = self.system_actions.launch_app(target)
                if success:
                    return f"Right away, sir. Launching {target}."
                else:
                    return f"I'm sorry sir, I could not launch {target}."

        if "volume to" in input_lower:
            import re
            match = re.search(r'volume to (\d+)', input_lower)
            if match:
                level = int(match.group(1))
                self.system_actions.adjust_volume(level)
                return f"Volume set to {level} percent, sir."

        # Pass to Gemini if not intercepted
        if not self.chat:
            return "I seem to be disconnected from my neural network, sir. Please check the API key."

        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I'm having trouble processing that right now, sir."
