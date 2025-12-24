from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DataModel(BaseModel):
    """схема входных данных для предсказания - все фичи квартиры"""
    
    # основное
    Цена: int
    Дата_публикации: str
    Город: str
    Субъект_РФ: str

    # класс жилья (one-hot)
    is_class_eco: bool
    is_class_comfort: bool
    is_class_business: bool
    is_class_elite: bool

    # тип дома
    is_brick: bool
    is_monolith: bool
    is_panel: bool
    is_new_build: bool

    # отделка
    has_finish_turnkey: bool
    has_finish_whitebox: bool
    has_finish_rough: bool

    # инфраструктура
    has_playground: bool
    has_parking_underground: bool
    has_parking_surface: bool
    has_parking_any: bool
    has_kindergarten: bool
    has_school: bool
    is_closed_yard: bool
    has_shops_nearby: bool
    has_fitness_nearby: bool

    # локация
    near_metro: bool
    near_park: bool
    near_water: bool

    # удобства
    has_concierge: bool
    has_storage_room: bool
    has_panoramic_windows: bool
    has_balcony: bool
    has_loggia: bool
    has_terrace: bool

    # финансы
    has_mortgage: bool
    is_assignment: bool
    has_discount: bool

    # расстояния до объектов (могут быть пустыми)
    dist_to_city_center: Optional[float]
    dist_to_school: Optional[float]
    dist_to_kindergarten: Optional[float]
    dist_to_park: Optional[float]
    dist_to_bus_stop: Optional[float]
    dist_to_supermarket: Optional[float]

    # региональная статистика
    Индекс_города: Optional[float]
    Курортный: bool
    Средняя_зп_в_городе_тыс_руб_2025: Optional[float]
    Население_2015: Optional[float]
    Динамика_населения_за_10_лет: Optional[float]
    ВРП_района_2023_млн_руб: Optional[str]

    # параметры квартиры
    Площадь: int
    Этаж: int
    Этажность_дома: int
    Цена_за_квадратный_метр: float
    Rooms_Count: int

    # тип недвижимости (one-hot)
    Property_Type_Квартира: bool
    Property_Type_Своб_планировка: bool
    Property_Type_Студия: bool

    class Config:
        populate_by_name = True


# схемы для истории 

class HistoryItemResponse(BaseModel):
    """одна запись из истории"""
    id: int
    timestamp: datetime
    input_data: str
    input_length: int
    prediction: Optional[float]
    status: str
    error_message: Optional[str]
    processing_time_ms: float

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    """ответ с историей - список записей + общее кол-во"""
    total_count: int
    items: List[HistoryItemResponse]


# схемы для статистики 

class ProcessingTimeStats(BaseModel):
    """статистика по времени обработки"""
    mean: float
    percentile_50: float
    percentile_95: float
    percentile_99: float


class InputDataStats(BaseModel):
    """статистика по входным данным"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_input_length: float
    min_input_length: int
    max_input_length: int


class StatsResponse(BaseModel):
    """полный ответ со статистикой"""
    processing_time: ProcessingTimeStats
    input_stats: InputDataStats


# схемы для авторизации 

class TokenResponse(BaseModel):
    """ответ с jwt токеном"""
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    """данные для логина"""
    username: str
    password: str


class MessageResponse(BaseModel):
    """просто текстовое сообщение"""
    message: str
