import re
import pandas as pd
from tqdm import tqdm

data = pd.read_excel("1.xlsx")
df = pd.DataFrame(data)

patterns = {
    "s_class_comfort": [r"\bкомфорт\b", r"комфорт[- ]класс", r"\bкомфортного\b"],
    "is_class_eco": [r"\bэконом\b", r"эконом[- ]класс", r"\bэкономичный\b"],
    "is_brick": [r"\bкирпичн", r"\bкирпичный\b", r"\bкирпич\b"],   # ловит кирпич, кирпичный, кирпича...
    "is_new_build": [r"новостро", r"новый жил", r"\bсдан\b", r"\bввод\b", r"\bсдач[аи]"], # новострой/сдан и др.
    "has_playground": [r"\bдетск(ая|ие)? площадк", r"площадк(а|и) для детей"],
    "has_parking": [r"подземн", r"парковк", r"стоянк"],
    "has_kindergarten": [r"детск(ий|ого|ая|ом)? сад", r"\bд\/с\b"],
    "has_school": [r"\bшкол", r"школ[аы]?"],
    "is_closed_yard": [r"закрыт(ый|ая)? двор", r"закрытый двор", r"закрыт двор"],
    "has_finishing_included": [r"всё включено", r"все включено", r"чистовая отделк", r"под отделк"]
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

