import joblib
import os

MODEL_PATH = "model/model.pkl"


def load_model():
    """
    Загружает артефакты модели: модель, scaler и список признаков.
    Возвращает словарь с ключами: model, scaler, feature_names, dist_cols
    """
    artifacts = joblib.load(MODEL_PATH)
    
    
    if isinstance(artifacts, dict) and 'model' in artifacts:
        return artifacts
    else:
        
        raise ValueError(
            "Старый формат модели! Перезапустите ноутбук Base_ML/base_ml.ipynb "
            "для сохранения модели в новом формате."
        )
