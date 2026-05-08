import google.generativeai as genai

class AIReplyModule:
    def __init__(self, api_key: str, context_prompt: str):
        self.api_key = api_key
        self.context_prompt = context_prompt
        self.is_configured = bool(self.api_key and self.api_key.strip())
        
        if self.is_configured:
            try:
                genai.configure(api_key=self.api_key)
                # Using Gemini 1.5 Flash as it is fast and suitable for short chat replies
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Failed to configure Gemini: {e}")
                self.is_configured = False

    def generate_smart_reply(self, incoming_message: str) -> str:
        """
        Takes an incoming message from a WhatsApp lead, analyzes it,
        and generates an appropriate response based on the bot context.
        """
        if not self.is_configured:
            return ""

        try:
            # Construct the prompt with context
            prompt = (
                f"Context/Instructions for you: {self.context_prompt}\n\n"
                f"You are receiving a message from a client on WhatsApp.\n"
                f"Client's message: '{incoming_message}'\n\n"
                f"Draft a short, polite, and helpful response in Bengali (or English if the user spoke English). "
                f"Do not include placeholders. Reply as if you are directly messaging them back."
            )
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
            return ""
        except Exception as e:
            print(f"Error generating AI reply: {e}")
            return ""
