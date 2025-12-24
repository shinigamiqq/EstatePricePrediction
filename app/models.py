from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database import Base


class RequestHistory(Base):
    """таблица для хранения истории запросов к модели"""
    __tablename__ = "request_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # входной json целиком (чтоб можно было посмотреть что отправляли)
    input_data = Column(Text, nullable=False)
    input_length = Column(Integer, nullable=False)  # длина json-а для статистики
    
    # результат предсказания
    prediction = Column(Float, nullable=True)
    status = Column(String(50), nullable=False)  # success или error
    error_message = Column(Text, nullable=True)
    
    # сколько мс заняла обработка
    processing_time_ms = Column(Float, nullable=False)
