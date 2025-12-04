
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = os.environ.get("SKILL_MODEL_PATH", "skill_model.pkl")

class SkillClassifier:
    def __init__(self):
        self.vec = None
        self.clf = None
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.vec, self.clf = pickle.load(f)
            except Exception:
                self._init_dummy()
        else:
            self._init_dummy()

    def _init_dummy(self):
       
        self.vec = TfidfVectorizer(ngram_range=(1,2), max_features=2000)
        self.clf = LogisticRegression()
        

    def predict(self, text: str) -> str:
        try:
            X = self.vec.transform([text])
            label = self.clf.predict(X)[0]
            return label
        except Exception:
            
            t = text.lower()
            if any(k in t for k in ["how do i", "not able", "don't know", "don't understand", "help me"]):
                return "beginner"
            if any(k in t for k in ["optimize", "best practice", "profiling", "benchmark"]):
                return "expert"
            return "intermediate"
