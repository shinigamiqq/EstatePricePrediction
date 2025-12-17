from pydantic import BaseModel
from typing import Optional


class DataModel(BaseModel):
    # Основные характеристики
    Цена: int
    Дата_публикации: str
    Город: str
    Субъект_РФ: str

    # Классы жилья
    is_class_eco: bool
    is_class_comfort: bool
    is_class_business: bool
    is_class_elite: bool

    # Тип дома
    is_brick: bool
    is_monolith: bool
    is_panel: bool
    is_new_build: bool

    # Отделка
    has_finish_turnkey: bool
    has_finish_whitebox: bool
    has_finish_rough: bool

    # Инфраструктура
    has_playground: bool
    has_parking_underground: bool
    has_parking_surface: bool
    has_parking_any: bool
    has_kindergarten: bool
    has_school: bool
    is_closed_yard: bool
    has_shops_nearby: bool
    has_fitness_nearby: bool

    # Локация
    near_metro: bool
    near_park: bool
    near_water: bool

    # Удобства
    has_concierge: bool
    has_storage_room: bool
    has_panoramic_windows: bool
    has_balcony: bool
    has_loggia: bool
    has_terrace: bool

    # Финансы и условия
    has_mortgage: bool
    is_assignment: bool
    has_discount: bool

    # Расстояния
    dist_to_city_center: Optional[float]
    dist_to_school: Optional[float]
    dist_to_kindergarten: Optional[float]
    dist_to_park: Optional[float]
    dist_to_bus_stop: Optional[float]
    dist_to_supermarket: Optional[float]

    # Региональная статистика
    Индекс_города: Optional[float]
    Курортный: bool
    Средняя_зп_в_городе_тыс_руб_2025: Optional[float]
    Население_2015: Optional[float]
    Динамика_населения_за_10_лет: Optional[float]
    ВРП_района_2023_млн_руб: Optional[str]

    # Квартира
    Площадь: int
    Этаж: int
    Этажность_дома: int
    Цена_за_квадратный_метр: float
    Rooms_Count: int

    # Тип недвижимости
    Property_Type_Квартира: bool
    Property_Type_Своб_планировка: bool
    Property_Type_Студия: bool

    class Config:
        allow_population_by_field_name = True

