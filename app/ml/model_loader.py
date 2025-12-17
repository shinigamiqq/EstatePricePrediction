import joblib

MODEL_PATH = "model/model.pkl"

def load_model():
    return joblib.load(MODEL_PATH)

