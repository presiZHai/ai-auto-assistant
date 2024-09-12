from transformers import pipeline
import warnings

warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")

class TurnTakingModel:
    def __init__(self):
        self.nlp = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            revision="af0f99b"
        )
        
        self.silence_threshold = 0.5  # seconds
        self.confidence_threshold = 0.8

    def should_respond(self, transcription, silence_duration):
        if silence_duration >= self.silence_threshold:
            sentiment = self.nlp(transcription)[0]
            
            if sentiment['score'] > self.confidence_threshold and sentiment['label'] != 'NEUTRAL':
                return True
        
        return False