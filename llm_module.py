import os
from dotenv import load_dotenv
import openai

class LLMModule:
    def __init__(self):
        load_dotenv()  # This loads the variables from .env
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for a car dealership."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error in LLM response generation: {e}")
            return None