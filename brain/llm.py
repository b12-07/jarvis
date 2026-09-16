import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, JARVIS_SYSTEM_PROMPT, MODEL_NAME
from actions.system import SystemActions
from actions.developer import execute_command, read_file, write_file
from plugins import load_all_plugins
from config import APP_ALIASES

class JarvisBrain:
    def __init__(self):
        self.system_actions = SystemActions(APP_ALIASES)
        self.chat = None
        self.client = None

        # Gather basic system and developer tools
        base_tools = [
            self.system_actions.get_system_metrics,
            self.system_actions.launch_app,
            self.system_actions.adjust_volume,
            execute_command,
            read_file,
            write_file
        ]

        # Dynamically load all tools from the plugins directory
        plugin_tools = load_all_plugins()
        self.tools = base_tools + plugin_tools

        self.current_model = MODEL_NAME

        # Only initialize if we have an API key (allows testing without key)
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.init_chat(self.current_model)
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")

    def init_chat(self, model_name: str, previous_history=None):
        if not self.client:
            return

        try:
            self.current_model = model_name
            self.chat = self.client.chats.create(
                model=model_name,
                history=previous_history,
                config=types.GenerateContentConfig(
                    system_instruction=JARVIS_SYSTEM_PROMPT,
                    temperature=0.7,
                    tools=self.tools
                )
            )
            print(f"[Brain] Chat session initialized with model: {model_name}")
        except Exception as e:
            print(f"Failed to initialize chat: {e}")

    def process_input(self, user_input: str) -> str:
        """Processes user input using Gemini with retry and fallback logic."""
        if not self.chat:
            return "Sinir ağından bağlantım kopmuş gibi görünüyor, efendim. Lütfen API anahtarını kontrol edin."

        import time
        from google.genai.errors import APIError

        max_retries = 3
        delay = 1.0

        for attempt in range(max_retries):
            try:
                response = self.chat.send_message(user_input)
                if response.text:
                    return response.text
                else:
                    return "Araç çalıştırıldı, efendim. Görevi tamamladım."

            except APIError as e:
                status_code = getattr(e, 'status', None)
                err_msg = str(e)
                # Check for 503 Service Unavailable or general network unavailability
                if status_code == "UNAVAILABLE" or "503" in err_msg or "unavailable" in err_msg.lower():
                    print(f"[Brain] Attempt {attempt+1}/{max_retries} failed with 503 UNAVAILABLE. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2.0 # Exponential backoff
                else:
                    # Non-503 API error, break loop and return error
                    print(f"Gemini API Error: {e}")
                    return "İsteğinizi işlerken bir API hatası oluştu, efendim."
            except Exception as e:
                print(f"Unexpected Error during generation: {e}")
                return "Şu anda bunu işlemekte zorlanıyorum, efendim. Beklenmedik bir hata oluştu."

        # If we exhausted retries on the current model, attempt a fallback
        if self.current_model != "gemini-2.5-flash":
            print(f"[Brain] Model {self.current_model} is unresponsive. Falling back to gemini-2.5-flash...")
            old_history = self.chat.get_history() if hasattr(self.chat, 'get_history') else None
            self.init_chat("gemini-2.5-flash", previous_history=old_history)

            # One final attempt with the fallback model
            try:
                response = self.chat.send_message(user_input)
                if response.text:
                    return response.text
                return "Araç çalıştırıldı, efendim. Görevi tamamladım."
            except Exception as e:
                print(f"[Brain] Fallback model also failed: {e}")
                return "Bağlantı denemelerim başarısız oldu efendim. Google sunucuları şu anda yanıt vermiyor."

        return "Bağlantı denemelerim başarısız oldu efendim. Google sunucuları şu anda yanıt vermiyor."
