import streamlit as st
import sounddevice as sd
import soundfile as sf
import tempfile
import numpy as np
import os
from stt_module import STTModule
from turn_taking_model import TurnTakingModel
from llm_module import LLMModule
from tts_module import TTSModule
import time

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'active' not in st.session_state:
    st.session_state.active = False

# Streamlit UI
st.title("Car Dealer AI Voice Agent")

# Initialize modules
try:
    stt_module = STTModule()
    turn_taking_model = TurnTakingModel()
    llm_module = LLMModule()
    tts_module = TTSModule()
except Exception as e:
    st.error(f"Error initializing modules. Please check your .env file and API keys. Error: {e}")
    st.stop()

# Start or stop the conversation
if st.button("Start/Stop Conversation"):
    st.session_state.active = not st.session_state.active

# Audio recording function
def record_audio(duration=5, fs=16000):
    st.write("Listening...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return recording

# Main interaction loop
while st.session_state.active:
    # Record audio
    audio_data = record_audio()

    # Save audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        sf.write(temp_audio.name, audio_data, 16000)
        temp_audio_path = temp_audio.name

    # Transcribe audio
    transcription = stt_module.transcribe(temp_audio_path)
    os.unlink(temp_audio_path)

    if transcription:
        st.write(f"User: {transcription}")
        st.session_state.conversation.append(f"User: {transcription}")

        # Check if AI should respond
        if turn_taking_model.should_respond(transcription, 0.5):  # Assume 0.5s silence
            # Show visual indicator when AI is responding
            st.image("sound_wave.gif")  # Use your animated GIF file

            response = llm_module.generate_response(transcription)
            st.write(f"AI: {response}")
            st.session_state.conversation.append(f"AI: {response}")

            # Generate AI response audio
            audio_response = tts_module.synthesize_speech(response)
            if audio_response:
                try:
                    # **Debugging: Check Audio Data Returned**
                    st.write(f"Audio Response Type: {type(audio_response)}")
                    st.write(f"Audio Response Length: {len(audio_response) if hasattr(audio_response, '__len__') else 'N/A'}")

                    # Write audio to file to check its content
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                        temp_audio.write(audio_response)
                        temp_audio.flush()
                        temp_audio_path = temp_audio.name
                    
                    # Play the audio response
                    data, samplerate = sf.read(temp_audio_path, dtype='float32')
                    sd.play(data, samplerate=samplerate)
                    sd.wait()
                    os.unlink(temp_audio_path)
                except Exception as e:
                    st.error(f"Error processing audio response: {e}")
                    st.write("Unable to play audio. Here's the text response:")
                    st.write(response)

    time.sleep(1)  # Small delay to avoid excessive loop speed

# Display conversation history
st.subheader("Conversation History")
for message in st.session_state.conversation:
    st.text(message)