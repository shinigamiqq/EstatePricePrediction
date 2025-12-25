import numpy as np
import pandas as pd


def run_model(artifacts: dict, data: dict):
    
    try:
        model = artifacts['model']
        scaler = artifacts['scaler']
        feature_names = artifacts['feature_names']
        dist_cols = artifacts['dist_cols']
        
        # DataFrame 
        df = pd.DataFrame([data])
        
        # Логарифмируем расстояния 
        for col in dist_cols:
            if col in df.columns:
                df[f'{col}_log'] = np.log1p(df[col].fillna(0))
            else:
                df[f'{col}_log'] = 0.0
        
        # Удаляем колонки, которые не нужны для предсказания
        cols_to_drop = ['Площадь', 'Дата_публикации', 'Дата публикации',
                        'Цена', 'Цена_log', 'Цена_за_квадратный_метр', 
                        'Цена_за_квадратный_метр_log'] + dist_cols
        
        for col in cols_to_drop:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # One-hot encoding 
        if 'Город' in df.columns:
            df = pd.get_dummies(df, columns=['Город'], drop_first=True)
        if 'Субъект_РФ' in df.columns:
            df = pd.get_dummies(df, columns=['Субъект_РФ'], drop_first=True)
        if 'Субъект РФ' in df.columns:
            df = pd.get_dummies(df, columns=['Субъект РФ'], drop_first=True)
        
        # Приведём к тем же признакам, что и при обучении
        missing_cols = {col: 0 for col in feature_names if col not in df.columns}
        if missing_cols:
            missing_df = pd.DataFrame([missing_cols])
            df = pd.concat([df, missing_df], axis=1)
        
        # только нужные колонки 
        df = df[feature_names]
        
        # Масштабирование через обученный scaler
        X_scaled = scaler.transform(df.values)
        
        # Предсказание 
        prediction_log = model.predict(X_scaled)
        
        # Обратное преобразование из логарифма
        prediction_real = float(np.expm1(prediction_log[0]))
        
        print(f"Prediction (log): {prediction_log[0]:.4f}, Real: {prediction_real:.2f} rub/m2")
        
        return {
            "prediction": prediction_real
        }
        
    except Exception as e:
        print(f"Inference error: {e}")
        import traceback
        traceback.print_exc()
        return None
