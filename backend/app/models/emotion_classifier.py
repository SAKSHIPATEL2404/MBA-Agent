# backend/app/models/emotion_classifier.py
# Very simple keyword-based emotion classifier for MVP.
# Replace with HuggingFace finetuned model in production.

class EmotionClassifier:
    def __init__(self):
        # could load a model here
        pass

    def predict(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["angry", "frustrat", "frustration", "pissed", "hate", "annoy"]):
            return "frustrated"
        if any(w in t for w in ["confus", "dont understand", "don't understand", "lost", "stuck"]):
            return "confused"
        if any(w in t for w in ["happy", "great", "thanks", "thank you", "awesome"]):
            return "happy"
        return "neutral"
