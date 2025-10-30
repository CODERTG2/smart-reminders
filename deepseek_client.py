import os
import requests
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


class DeepseekClient:
    """Client for Deepseek R1 via OpenRouter API."""
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-r1"
    
    def chat(self, messages, model=None):
        """
        Send a chat completion request to DeepSeek R1 via OpenRouter.
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/CODERTG2/NewsDash",
            "X-Title": "NewsDash"
        }

        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            if response.status_code != 200:
                print("\n--- DEBUG INFO ---")
                print("Status:", response.status_code)
                print("Response Text:", response.text)
                print("------------------\n")
            response.raise_for_status()
            data = response.json()
            return {
                "message": {
                    "content": data["choices"][0]["message"]["content"]
                }
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API request failed: {e}")
