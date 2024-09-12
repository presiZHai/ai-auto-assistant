import os
import logging
import subprocess
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

class STTModule:
    def __init__(self):
        """Initialize the STTModule with Google Cloud credentials."""
        load_dotenv()  # Load environment variables
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_PATH')
        
        if not credentials_path or not os.path.isfile(credentials_path):
            raise ValueError("Invalid or missing GOOGLE_APPLICATION_CREDENTIALS_PATH environment variable.")
        
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.client = speech.SpeechClient(credentials=self.credentials)
    
    def convert_audio(self, input_file, output_file):
        """Convert audio to the required format using ffmpeg."""
        command = [
            'ffmpeg', '-i', input_file,
            '-ar', '16000',  # Set sample rate to 16000 Hz
            '-ac', '1',      # Set number of audio channels to 1 (mono)
            '-f', 'wav',     # Output format
            output_file
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error converting audio: {e}")
            raise
    
    def transcribe(self, audio_file):
        """Transcribe the given audio file to text."""
        # Temporary file for the converted audio
        converted_audio_file = 'converted_audio.wav'
        
        # Convert audio to the required format
        try:
            self.convert_audio(audio_file, converted_audio_file)
        except Exception as e:
            logging.error(f"Audio conversion failed: {e}")
            return None

        try:
            with open(converted_audio_file, "rb") as audio:
                content = audio.read()
        except FileNotFoundError:
            logging.error(f"File not found: {converted_audio_file}")
            return None
        except IOError as e:
            logging.error(f"Error reading file: {e}")
            return None
        finally:
            if os.path.exists(converted_audio_file):
                os.remove(converted_audio_file)
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        
        try:
            response = self.client.recognize(config=config, audio=audio)
        except Exception as e:
            logging.error(f"Error calling Google Speech-to-Text API: {e}")
            return None

        transcript = ' '.join([result.alternatives[0].transcript for result in response.results])
        return transcript