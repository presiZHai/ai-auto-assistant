import os
from google.cloud import texttospeech
from google.oauth2 import service_account
from dotenv import load_dotenv

class TTSModule:
    def __init__(self):
        load_dotenv()  # Load environment variables
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PATH')
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.client = texttospeech.TextToSpeechClient(credentials=self.credentials)
    
    def synthesize_speech(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", 
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content