import re
import pandas as pd
from tqdm import tqdm

data = pd.read_excel("1.xlsx")
df = pd.DataFrame(data)

patterns = {
    #  Класс Жилья 
    "is_class_eco": [r"\bэконом\b", r"эконом[- ]класс", r"\bэкономичный\b"],
    "is_class_comfort": [r"\bкомфорт\b", r"комфорт[- ]класс", r"\bкомфортного\b"],
    "is_class_business": [r"\bбизнес\b", r"бизнес[- ]класс", r"\bpremium\b", r"\bпремиум\b"],
    "is_class_elite": [r"\bэлитн", r"de luxe", r"deluxe", r"\bделюкс\b", r"клубный дом"],
    
    #  Материалы и Тип дома 
    "is_brick": [r"\bкирпичн", r"\bкирпичный\b", r"\bкирпич\b"],
    "is_monolith": [r"\bмонолит", r"\bмонолитн", r"монолитно-кирпичн"],
    "is_panel": [r"\bпанельн", r"\bпанель\b"],
    "is_new_build": [r"новостро", r"новый жил", r"\bсдан\b", r"\bввод\b", r"\bсдач[аи]", r"от застройщика"],

    #  Отделка  
    "has_finish_turnkey": [r"чистовая отделк", r"с ремонтом", r"под ключ", r"заезжай и живи", r"дизайнерский ремонт", r"всё включено"],
    "has_finish_whitebox": [r"white box", r"whitebox", r"предчистовая"],
    "has_finish_rough": [r"черновая", r"\bпод отделку\b", r"без отделки", r"\bстяжка\b"], # \b чтобы не поймать "подземный"

    #  Инфраструктура  
    "has_playground": [r"\bдетск(ая|ие)? площадк", r"площадк(а|и) для детей"],
    "has_parking_underground": [r"подземн(ый|ая)? (паркинг|парковк|стоянк)"],
    "has_parking_surface": [r"наземн(ый|ая)? (паркинг|парковк|стоянк)", r"гостевая парковка"],
    "has_parking_any": [r"парковк", r"паркинг", r"стоянк", r"парковочное место"], # Общий признак, если не уточнено
    "has_kindergarten": [r"детск(ий|ого|ая|ом)? сад", r"\bд\/с\b"],
    "has_school": [r"\bшкол", r"школ[аы]?"],
    "is_closed_yard": [r"закрыт(ый|ая)? двор", r"двор без машин", r"огороженная территория"],
    "has_shops_nearby": [r"магазин", r"тц", r"торговый центр", r"гипермаркет", r"супермаркет"],
    "has_fitness_nearby": [r"фитнес", r"спортзал", "бассейн"],

    #  Окружение 
    "near_metro": [r"\bметро\b", r"станция метро"],
    "near_park": [r"\bпарк", r"\bсквер", r"\bлес", r"лесопарк", r"зелен(ая|ый) район"],
    "near_water": [r"\bрек[аи]", r"\bозер", r"\bпруд", r"\bнабережная", r"вид на вод"],

    #  Характеристики дома/квартиры 
    "has_concierge": [r"консьерж", r"\bохрана\b", r"\bресепшн\b", r"lobby", r"\bлобби\b", r"видеонаблюдение"],
    "has_storage_room": [r"кладов", r"колясочн"],
    "has_panoramic_windows": [r"панорамн", r"окна в пол", r"видов(ые)? окн"],
    "has_balcony": [r"\bбалкон"],
    "has_loggia": [r"\bлоджия"],
    "has_terrace": [r"\bтеррас", r"\bпатио"],

    #  Условия продажи 
    "has_mortgage": [r"ипотек", r"семейная ипотека", r"господдержк"],
    "is_assignment": [r"переуступк", r"уступка прав"],
    "has_discount": [r"\bскидк", r"\bакция", r"спецпредложение"],
}

def contains_any(text: str, pats) -> bool:
    if not isinstance(text, str):
        return False
    for p in pats:
        if re.search(p, text, flags=re.I | re.U):
            return True
    return False

for col, pats in tqdm(patterns.items()):
    df[col] = df["Описание"].apply(lambda x: contains_any(x, pats))

print(df.loc[:, ["Описание"] + list(patterns.keys())].T)

