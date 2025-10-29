import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from tqdm import tqdm

tqdm.pandas()

df = pd.read_excel("1.xlsx")

texts = df["Описание"].fillna("").astype(str)

vectorizer = TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 2),
    stop_words=["и", "в", "на", "с", "по", "для", "от", "что", "как"]
)
X_tfidf = vectorizer.fit_transform(texts)
feature_names = vectorizer.get_feature_names_out()

patterns = {
    "is_class_comfort": [r"\bкомфорт", r"комфорт[- ]класс", r"\bкомфортного"],
    "is_class_eco": [r"\bэконом", r"эконом[- ]класс", r"\bэкономичный"],
    "is_brick": [r"\bкирпич", r"кирпичный"],
    "is_new_build": [r"новостро", r"новый жил", r"\bсдан\b", r"\bввод", r"\bсдач[аи]"],
    "has_playground": [r"детск(ая|ие)? площадк", r"площадк(а|и) для детей"],
    "has_parking": [r"подземн", r"парковк", r"стоянк"],
    "has_kindergarten": [r"детск(ий|ого|ая|ом)? сад", r"\bд\/с\b"],
    "has_school": [r"\bшкол", r"школ[аы]?"],
    "is_closed_yard": [r"закрыт(ый|ая)? двор", r"закрытый двор", r"закрыт двор"],
    "has_finishing_included": [r"всё включено", r"все включено", r"чистовая отделк", r"под отделк"]
}

def contains_any(text, pats):
    if not isinstance(text, str):
        return False
    for p in pats:
        if re.search(p, text, flags=re.I | re.U):
            return True
    return False

for col, pats in patterns.items():
    df[col] = texts.progress_apply(lambda x: contains_any(x, pats))

print(df[[ "Описание" ] + list(patterns.keys())].head())

df.to_excel("1_with_features.xlsx", index=False)

