import numpy as np


FEATURE_ORDER = [
    "Цена",
    "is_class_eco",
    "is_class_comfort",
    "is_class_business",
    "is_class_elite",

    "is_brick",
    "is_monolith",
    "is_panel",
    "is_new_build",

    "has_finish_turnkey",
    "has_finish_whitebox",
    "has_finish_rough",

    "has_playground",
    "has_parking_underground",
    "has_parking_surface",
    "has_parking_any",
    "has_kindergarten",
    "has_school",
    "is_closed_yard",
    "has_shops_nearby",
    "has_fitness_nearby",

    "near_metro",
    "near_park",
    "near_water",

    "has_concierge",
    "has_storage_room",
    "has_panoramic_windows",
    "has_balcony",
    "has_loggia",
    "has_terrace",

    "has_mortgage",
    "is_assignment",
    "has_discount",

    "dist_to_city_center",
    "dist_to_school",
    "dist_to_kindergarten",
    "dist_to_park",
    "dist_to_bus_stop",
    "dist_to_supermarket",

    "Индекс_города",
    "Курортный",
    "Средняя_зп_в_городе_тыс_руб_2025",
    "Население_2015",
    "Динамика_населения_за_10_лет",

    "Площадь",
    "Этаж",
    "Этажность_дома",
    "Цена_за_квадратный_метр",
    "Rooms_Count",

    "Property_Type_Квартира",
    "Property_Type_Своб_планировка",
    "Property_Type_Студия"
]


def run_model(model, data: dict):
    try:
        row = []

        for feature in FEATURE_ORDER:
            value = data.get(feature)

            if isinstance(value, bool):
                value = int(value)

            if value is None:
                value = 0

            row.append(value)

        X = np.array([row], dtype=float)

        prediction = model.predict(X)
        print(prediction)

        return {
            "prediction": float(prediction[0])
        }

    except Exception as e:
        print(f"Inference error: {e}")
        return None
