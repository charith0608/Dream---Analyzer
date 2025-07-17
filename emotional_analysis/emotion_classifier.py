# emotion_analysis/emotion_classifier.py

from transformers import pipeline

class EmotionClassifier:
    def __init__(self):
        # Emotion Detection
        self.emotion_pipe = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion", top_k=3)

        # Symbol Recognition via NER
        self.ner_pipe = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

        # Intent Classification (placeholder for now)
        self.intent_pipe = pipeline("text-classification", model="facebook/bart-large-mnli")

    def predict(self, text: str):
        emotion_results = self.emotion_pipe(text)
        ner_results = self.ner_pipe(text)
        intent_results = self.intent_pipe(text, candidate_labels=["fear", "freedom", "love", "avoidance", "growth", "healing"])

        # Simplified output
        return {
            "emotions": {e['label']: round(e['score'], 2) for e in emotion_results},
            "symbols": [ent["word"] for ent in ner_results],
            "intent": sorted(intent_results, key=lambda x: x['score'], reverse=True)[0]['label']
        }
