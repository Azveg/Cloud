import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import BallTree
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline
import numpy as np
import re


df = pd.read_parquet('df.parquet')

# Векторизация текстов
# ----------------------------------------------------
# создаем объект, который будет преобразовывать короткие тексты в числовые векторы
vectorized = TfidfVectorizer()
# обучаем его на всех контекстах -> запоминаем частоту каждого слова
vectorized.fit(df.context_0)
# записываем в матрицу, сколько раз каждое слово встречалось в тексте
matrix_big = vectorized.transform(df.context_0)

# Сокращение размерности
# ------------------------------------------------
# алгоритм будет проецировать данные на 300-мерное пространство
svd = TruncatedSVD(n_components=300)
# коэф. этого преобразования выучиваются так, чтобы сохранить максимум информации об исходной матрице
svd.fit(matrix_big)
matrix_small = svd.transform(matrix_big)


# Поиск ближайших соседей
# ---------------------------------------
def softmax(x):
    proba = np.exp(-x)
    return proba / sum(proba)


class NeighborSampler(BaseEstimator):
    def __init__(self, k=5, temperature=1.0):
        self.k = k
        self.temperature = temperature

    def fit(self, X, y):
        self.tree_ = BallTree(X)
        self.y_ = np.array(y)

    def predict(self, X, random_state=None):
        distances, indices = self.tree_.query(X, return_distance=True, k=self.k)
        result = []
        for distance, index in zip(distances, indices):
            result.append(np.random.choice(index, p=softmax(distance * self.temperature)))
            return self.y_[result]


# соединяем методы векторизации, сокращения размерности и поиска соседей
ns = NeighborSampler()
ns.fit(matrix_small, df.reply)
pipe = make_pipeline(vectorized, svd, ns)


def answer(question):
    return re.sub('[^А-я,?!.\\s]', '', str(pipe.predict([question])))
