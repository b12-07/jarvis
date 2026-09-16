import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, JARVIS_SYSTEM_PROMPT, MODEL_NAME
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
                model=MODEL_NAME,
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

        # Intercept simple commands for system actions (added Turkish support)
        if "sistem durum" in input_lower or "cpu" in input_lower or "ram" in input_lower or "system stats" in input_lower:
            cpu, ram = self.system_actions.get_system_metrics()
            return f"Efendim, CPU kullanımı şu anda yüzde {cpu}, ve RAM kullanımı yüzde {ram} seviyesinde."

        if "aç" in input_lower or "başlat" in input_lower or "open" in input_lower or "launch" in input_lower:
            import re
            # Turkish syntax usually puts the verb at the end, e.g. "chrome'u aç" or "chrome aç"
            # We'll support both "aç chrome" and "chrome aç" for robustness
            match = re.search(r'(?:aç|başlat|open|launch)\s+(.+)|(.+?)\s+(?:aç|başlat|open|launch)', input_lower)
            if match:
                target = match.group(1) if match.group(1) else match.group(2)
                target = target.strip().strip('.').strip('?').replace("'u", "").replace("'ü", "").replace("'ı", "").replace("'i", "")
                success = self.system_actions.launch_app(target)
                if success:
                    return f"Hemen hallediyorum, efendim. {target} başlatılıyor."
                else:
                    return f"Özür dilerim efendim, {target} uygulamasını başlatamadım."

        if "sesi" in input_lower and "yap" in input_lower or "volume to" in input_lower:
            import re
            match = re.search(r'(?:sesi|volume to) %?(\d+)', input_lower.replace('yüzde ', ''))
            if match:
                level = int(match.group(1))
                self.system_actions.adjust_volume(level)
                return f"Ses seviyesi yüzde {level} olarak ayarlandı, efendim."

        # Pass to Gemini if not intercepted
        if not self.chat:
            return "Sinir ağından bağlantım kopmuş gibi görünüyor, efendim. Lütfen API anahtarını kontrol edin."

        try:
            response = self.chat.send_message(user_input)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Şu anda bunu işlemekte zorlanıyorum, efendim."
